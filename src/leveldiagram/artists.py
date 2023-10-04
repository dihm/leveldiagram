"""
Customized matplotlib artist primitives
"""

import matplotlib as mpl
from matplotlib.lines import Line2D
import numpy as np
import warnings

from typing import Optional, Any, Union, Literal, Collection, Dict, Tuple

from .utils import deep_update

affine = mpl.transforms.Affine2D


class EnergyLevel(Line2D):
    """
    Energy level artist.

    This object also implements a number of potential Text artists for labelling.
    It also includes helper methods for getting the exact coordinates of anchor points
    for connected coupling arrows and the like.
    """

    def __str__(self):
        if self._energy is None:
            return "EnergyLevel()"
        else:
            return "EnergyLevel((%g,%g))" % (self._xpos, self._energy)

    def __init__(
        self,
        energy: float,
        xpos: float,
        width: float,
        right_text: str = "",
        left_text: str = "",
        top_text: str = "",
        bottom_text: str = "",
        text_kw: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Parameters:
            energy (float): y-axis position of the level
            xpos (float): x-axis position of the level
            width (float): Width of the level line, in units of the x-axis
            right_text (str, optional): Text to put to the right of the level
            left_text (str, optional): Text to put to the left of the level
            top_text (str, optional): Text to put above the level
            bottom_text (str, optional): Text to put below the level
            text_kw (dict, optional): Dictionary of keyword-arguments passed to
                :class:`matplotlib:matplotlib.text.Text`
            kwargs: Passed to the :class:`matplotlib:matplotlib.lines.Line2D` constructor
        """

        self._energy = energy
        self._xpos = xpos
        self._width = width

        if text_kw is None:
            text_kw = {}
        # we'll update the position when the line data is set
        self.text_labels: Dict[str, mpl.text.Text] = {
            "right": mpl.text.Text(
                xpos + width / 2, energy, right_text, ha="left", va="center", **text_kw
            ),
            "left": mpl.text.Text(
                xpos - width / 2, energy, left_text, ha="right", va="center", **text_kw
            ),
            "top": mpl.text.Text(
                xpos, energy, top_text, ha="center", va="bottom", **text_kw
            ),
            "bottom": mpl.text.Text(
                xpos, energy, bottom_text, ha="center", va="top", **text_kw
            ),
        }
        """Text label objects to add to the level"""

        x = (xpos - width / 2, xpos + width / 2)
        y = (energy, energy)

        super().__init__(x, y, **kwargs)

    def get_center(self) -> np.ndarray:
        """
        Returns coordinates of the center of the level line.

        Returns:
            numpy.ndarray: x,y coordinates
        """

        return np.array((self._xpos, self._energy), dtype=float)

    def get_left(self) -> np.ndarray:
        """
        Returns coordinates of the left of the level line.

        Returns:
            numpy.ndarray: x,y coordinates
        """

        return np.array((self._xpos - self._width / 2, self._energy), dtype=float)

    def get_right(self) -> np.ndarray:
        """
        Returns coordinates of the right of the level line.

        Returns:
            numpy.ndarray: x,y coordinates
        """

        return np.array((self._xpos + self._width / 2, self._energy), dtype=float)

    def get_anchor(
        self, loc: Union[Literal["center", "left", "right"], Collection] = "center"
    ) -> np.ndarray:
        """
        Returns an anchor on the level in plot coordinates.

        Parameters:
            loc (str or collection of 2 elements): What reference point to return.
                `'center'`, `'left'`, `'right'` gives those points of the level.
                A 2-element iterable is interpreted as offsets from the center
                location.

        Raises:
            TypeError: If `loc` is not accepted string or a 2-element iterable.
        """

        if loc == "center":
            anchor = self.get_center()
        elif loc == "left":
            anchor = self.get_left()
        elif loc == "right":
            anchor = self.get_right()
        else:
            if len(loc) == 2:
                anchor = self.get_center() + np.array(loc)
            else:
                raise TypeError("loc must iterable of two elements if not using keys")

        return anchor

    def set_figure(self, figure):
        for side, label in self.text_labels.items():
            label.set_figure(figure)
        super().set_figure(figure)

    def set_axes(self, axes: mpl.axes.Axes):
        for side, label in self.text_labels.items():
            label.set_axes(axes)
        super().set_axes(axes)

    def set_transform(self, transform):
        """
        Overridden to add padding offsets to labels.
        """
        # pixel offsets
        pad = 6
        offsets = {
            "right": (pad, 0),
            "left": (-pad, 0),
            "top": (0, pad),
            "bottom": (0, -pad),
        }
        for side, label in self.text_labels.items():
            label.set_transform(transform + affine().translate(*offsets[side]))
        super().set_transform(transform)

    def set_data(self, x, y):

        super().set_data(x, y)

    def draw(self, renderer):

        super().draw(renderer)
        for side, label in self.text_labels.items():
            label.draw(renderer)


class Coupling(Line2D):
    """
    Coupling artist for showing couplings between levels.

    This artist is a conglomeration of artists.

    - :class:`Line2D <matplotlib:matplotlib.lines.Line2D>` for the actual coupling path
    - :class:`Polygon <matplotlib:matplotlib.patches.Polygon>` for the arrow heads
    - :class:`Text <matplotlib:matplotlib.text.Text>` for the label

    Sufficient methods are overridden from the base Line2D class to ensure
    the other artists are rendered whenever the main artist is rendered.
    """

    def __str__(self) -> str:

        return "Coupling((%g,%g)->(%g,%g))" % (*self._start, *self._stop)

    def __init__(
        self,
        start: Collection,
        stop: Collection,
        arrowsize: float,
        deflection: float = 0.0,
        waveamp: float = 0.0,
        halfperiod: float = 0,
        arrowratio: float = 1,
        tail: bool = False,
        arrow_kw: Optional[Dict[str, Any]] = None,
        label: str = "",
        label_offset: Literal["center", "left", "right"] = "center",
        label_rot: bool = False,
        label_flip: bool = False,
        label_kw: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Parameters:
            start (2-element collection): Coupling start location in data coordinates
            stop (2-element collection): Coupling end location in data coordinates
            arrowsize (float): Size of arrowheads in x-data coordinates
            deflection (float, optional): Amount to bend the center of the coupling arrow
                away from linear.
                Defined in y-coordintes. Default is 0 or no deflection.
            waveamp (float, optional): Amplitude of sine wave modulation of the coupling arrow.
                Defined in y-coordinates. Default is 0 or no waviness.
            halfperiod (float, optional): Length of half-period of sine modulation.
                Defined in x-coordinates.
                Both `waveamp` and `period` must be non-zero to get modulation.
                Default is 0 or no waviness.
            arrowratio (float, optional): Aspect ratio of the arrowhead.
                Default is 1 for equal aspect ratio.
            tail (bool, optional): Whether to draw an identical arrowhead at the coupling base.
                Default is False.
            arrow_kw (dict, optional): Dictionary of keyword arguments to pass to
                :class:`matplotlib:matplotlib.patches.Polygon` constructor.
                Note that keyword arguments provided to this function will clobber
                identical keys provided here.
            label (str, optional): Label string to apply to the coupling.
                Default is no label.
            label_offset (str, optional): Offset direction for the label.
                Options are `'center'`, `'left'`, and `'right'`.
                Default is center of the coupling line.
            label_rot (bool, optional): Label is justified along the coupling arrow axis if True.
                Default is False, so label is oriented along x-axis always.
            label_flip (bool, optional): Apply a 180 degree rotation to the label.
                Default is False.
            label_kw (dict, optional): Dictionary of keyword arguments to pass to the
                :class:`matplotlib:matplotlib.text.Text` constructor.
            kwargs: Optional keyword arguments passed to the
                :class:`matplotlib:matplotlib.lines.Line2D` constructor and the
                :class:`matplotlib:matplotlib.patches.Polygon` constructor for the arrowhead.
                Note that `'color'` will be automatically changed to `'facecolor'` for
                the arrowhead to avoid extra lines.
        """

        if not isinstance(start, Collection) or not isinstance(stop, Collection):
            raise RuntimeError("x/y data must be a sequence of two elements")
        elif len(start) != 2 or len(stop) != 2:
            raise RuntimeError("x/y data must be a sequence of two elements")

        if arrow_kw is None:
            arrow_kw = {}
        if label_kw is None:
            label_kw = {}

        self._start = np.array(start)
        self._stop = np.array(stop)
        self._arrowsize = arrowsize
        self._arrowratio = arrowratio
        self._tail = tail
        self.tail = False

        self._deflection = deflection
        self._deflect = not np.isclose(deflection, 0.0)

        self._waveamp = waveamp
        self._halfperiod = halfperiod

        # set number of points to use when drawing lines
        self.npts = 100

        if arrowsize * arrowratio < waveamp:
            warnings.warn(
                "Wave amplitude is larger than arrowhead; result will look funny."
            )

        x0, y0 = self.init_path()
        super().__init__(x0, y0, **kwargs)

        # initialize arrowheads
        # use line kwargs to set arrow defaults
        arrow_kw.update(kwargs)
        # use facecolor instead of color
        color = arrow_kw.pop("color", None)
        if color is not None:
            arrow_kw["fc"] = color
        self.init_arrowheads(**arrow_kw)

        # initialize label text
        self.init_label(label, label_offset, label_rot, label_flip, **label_kw)

    def init_path(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculates the desired path for the line of the coupling.

        The returned path is a line relative to the x-axis of the correct length.
        Transforms are used to move and rotate this path to the end location.
        This method of making the couplings is a little convoluted,
        but it allows for simple definition of very general paths (line sine waves)
        without distortions.

        Returns
        -------
        x: numpy.ndarray
            x-coordinates of the data points for the un-rotated, un-translated path
        y: numpy.ndarray
            y-coordinates of the data points for the un-rotated, un-translated path
        """

        vec = self._stop - self._start
        dist = np.sqrt(vec.dot(vec))
        self._dist = dist
        self._ang = np.arctan2(*vec[::-1])

        h = self._deflection

        # convert half-periods
        try:
            omega = np.pi / self._halfperiod
        except ZeroDivisionError:
            omega = 0.0
        
        if self._deflect:

            if h > dist/2:
                warnings.warn("Maximum deflection exceded "
                              "(deflection > half vector length). "
                              "Behavior poorly defined.")
        
            r = (dist**2+4*h**2)/(8*h)
            theta_center = 2*np.arcsin(dist/2/r)
            # accounts for shortened path from arrowheads
            theta_shim = 2*np.arcsin(self._arrowsize/2/r)
            phi = theta_center/2
            self._phi = phi
            # accounts for shortened path when rotating arrowheads
            self._phi_shim = phi - theta_shim/2

            if self._tail:
                thetas = np.linspace(theta_shim, theta_center-theta_shim, self.npts)
                theta0 = theta_center-theta_shim*2
            else:
                thetas = np.linspace(0, theta_center - theta_shim, self.npts)
                theta0 = theta_center-theta_shim

            xc = ((r+self._waveamp*
                   np.sin(omega*r*theta_center*thetas/theta0))
                  * np.sin(thetas-phi)
                  + r*np.sin(phi))
            yc = ((r+self._waveamp*
                  np.sin(omega*r*theta_center*thetas/theta0))
                  * np.cos(thetas-phi)
                  - r*np.cos(phi))
        
            return xc, yc
        
        else:
            
            if self._tail:
                x0 = np.linspace(self._arrowsize, dist - self._arrowsize, self.npts)
                op0 = omega * self._arrowsize*2
            else:
                x0 = np.linspace(0, dist - self._arrowsize, self.npts)
                op0 = omega * self._arrowsize
                
            y0 = self._waveamp * np.sin(omega*x0 + op0)
                
            return x0, y0

    def init_arrowheads(self, **kwargs):
        """
        Creates the arrowhead(s) for the coupling as matplotlib polygon objects.

        Parameters:
            kwargs: Optional keyword arguments to pass to the
                :class:`matplotlib:matplotlib.patches.Polygon` constructor.
        """

        verts0 = np.array([[-1, 0.5], [-1, -0.5], [0, 0], [-1, 0.5]])
        # set aspect ratio of arrow
        verts0[:,1] *= self._arrowratio
        
        if self._deflect:
            verts_head = verts0 @ self._rotation_matrix(self._phi_shim)
            self.head = mpl.patches.Polygon(verts_head, closed=False, **kwargs)
            if self._tail:
                verts_tail = verts0 @ self._rotation_matrix(-self._phi_shim)
                self.tail = mpl.patches.Polygon(verts_tail, closed=False, **kwargs)
                
        else:
            self.head = mpl.patches.Polygon(verts0, closed=False, **kwargs)
            
            if self._tail:
                self.tail = mpl.patches.Polygon(verts0, closed=False, **kwargs)

    def _rotation_matrix(self, theta):
        
        rot= np.array([[np.cos(theta), -np.sin(theta)],
                       [np.sin(theta), np.cos(theta)]])
        
        return rot

    def init_label(
        self,
        label: str,
        label_offset: Literal["center", "right", "left"],
        label_rot: bool,
        label_flip: bool,
        **label_kw
    ):
        """
        Creates the coupling label text object.

        Parameters:
            label (str): Label string to apply to the coupling.
            label_offset (str): Offset direction for the label.
                Options are `'center'`, `'left'`, and `'right'`.
            label_rot (bool): Label will be justified along the coupling arrow axis if True.
            label_flip (bool): Apply a 180 degree rotation to the label.
            label_kw: Keyword arguments to pass to the
                :class:`matplotlib:matplotlib.text.Text` constructor.
        """

        # define default softbackground for text
        bbox_defaults = {
            "boxstyle": "round,pad=0.05",
            "fc": "w",
            "ec": "none",
            "alpha": 0.5,
        }
        bbox_dict = label_kw.pop("bbox", {})
        bbox_dict = deep_update(bbox_defaults, bbox_dict)
        label_kw["bbox"] = bbox_dict

        if label_offset == "center":
            label_ha = "center"
        # flip to match anchor ha settings
        elif label_offset == "right":
            label_ha = "left"
        elif label_offset == "left":
            label_ha = "right"
        self.text = mpl.text.Text(
            self._dist / 2,
            self._deflection,
            label,
            ha=label_ha,
            va="center",
            transform_rotates_text=label_rot,
            rotation=label_flip * 180,
            **label_kw
        )
        # give space for non-centered text
        self.text_shift = np.array([0, 0])
        if not label_rot:
            pad = self.text.get_fontsize() / 2  # in points
        else:
            pad = 0
        if label_ha == "left":
            self.text_shift[0] += pad
        elif label_ha == "right":
            self.text_shift[0] -= pad

    def set_figure(self, figure):

        self.head.set_figure(figure)
        if self.tail:
            self.tail.set_figure(figure)
        self.text.set_figure(figure)
        super().set_figure(figure)

    def set_axes(self, axes):

        self.head.set_axes(axes)
        if self.tail:
            self.tail.set_axes(axes)
        self.text.set_axes(axes)
        super().set_axes(axes)

    def set_transform(self, transform):

        head_transform = (
            affine()
            .scale(self._arrowsize, self._arrowsize)
            .rotate(self._ang)
            .translate(*self._stop)
        )
        self.head.set_transform(head_transform + transform)

        if self.tail:
            tail_transform = (
                affine()
                .scale(self._arrowsize, self._arrowsize)
                .rotate(self._ang + np.pi)
                .translate(*self._start)
            )
            self.tail.set_transform(tail_transform + transform)

        # want to translate text shim in points
        text_shim = affine().translate(*self.text_shift)
        # want main translate in 'data' coords
        text_transform = affine().rotate(self._ang).translate(*self._start)
        self.text.set_transform(text_transform + transform + text_shim)

        # lw_shim = affine().scale(
        line_transform = affine().rotate(self._ang).translate(*self._start)
        super().set_transform(line_transform + transform)

    def draw(self, renderer):

        super().draw(renderer)
        self.head.draw(renderer)
        if self.tail:
            self.tail.draw(renderer)
        self.text.draw(renderer)
