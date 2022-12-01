"""
Customized matplotlib artist primitives
"""

import matplotlib as mpl
from matplotlib.lines import Line2D
import numpy as np
import warnings

affine = mpl.transforms.Affine2D


class EnergyLevel(Line2D):
    """
    Energy level artist.
    """

    def __str__(self):
        if self._energy is None:
            return "EnergyLevel()"
        else:
            return "EnergyLevel((%g,%g))" % (self._xpos, self._energy)

    def __init__(self, energy, xpos, width,
                 right_text='', left_text='',
                 top_text='', bottom_text='',
                 text_kw = {},
                 **kwargs):
        """
        
        Parameters
        ----------

        energy: float
            y-axis position of the level
        xpos: float
            x-axis position of the level
        width: float
            Width of the level line, in units of the x-axis
        right_text: str, optional
            Text to put to the right of the level
        left_text: str, optional
            Text to put to the left of the level
        top_text: str, optional
            Text to put above the level
        bottom_text: str, optional
            Text to put below the level
        text_kw: dict, optional
            Dictionary of keyword-arguments passed to matplotlib.text.Text
        kwargs:
            Passed to the Line2D constructor
        """

        self._energy = energy
        self._xpos = xpos
        self._width = width
        # we'll update the position when the line data is set
        self.text_labels = {'right': mpl.text.Text(xpos + width/2,
                                                   energy, right_text,
                                                   ha='left', va='center', **text_kw),
                            'left': mpl.text.Text(xpos - width/2,
                                                  energy, left_text,
                                                  ha='right', va='center', **text_kw),
                            'top': mpl.text.Text(xpos,
                                                 energy, top_text,
                                                 ha='center', va='bottom', **text_kw),
                            'bottom': mpl.text.Text(xpos,
                                                    energy, bottom_text,
                                                    ha='center', va='top', **text_kw)}

        x = (xpos - width/2, xpos + width/2)
        y = (energy, energy)

        super().__init__(x, y, **kwargs)

    def get_center(self):

        return np.array((self._xpos, self._energy), dtype=float)

    def get_left(self):

        return np.array((self._xpos - self._width/2, self._energy), dtype=float)

    def get_right(self):

        return np.array((self._xpos + self._width/2, self._energy), dtype=float)

    def get_anchor(self, loc='center'):

        if loc == 'center':
            anchor = self.get_center()
        elif loc == 'left':
            anchor = self.get_left()
        elif loc == 'right':
            anchor = self.get_right()
        else:
            if len(loc) == 2:
                loc = np.array(loc)
                anchor = self.get_center() - loc
            else:
                raise TypeError('loc must iterable of two elements if not using keys')
        
        return anchor


    def set_figure(self, figure):
        for side, label in self.text_labels.items():
            label.set_figure(figure)
        super().set_figure(figure)

    def set_axes(self, axes):
        for side, label in self.text_labels.items():
            label.set_axes(axes)
        super().set_axes(axes)

    def set_transform(self, transform):
        # pixel offsets
        pad = 6
        offsets = {'right':(pad, 0),
                   'left':(-pad, 0),
                   'top':(0, pad),
                   'bottom':(0, -pad)}
        for side, label in self.text_labels.items():
            label.set_transform(transform + affine().translate(*offsets[side]))
        super().set_transform(transform)

    def set_data(self, x, y):

        super().set_data(x, y)

    def draw(self, renderer):
        # draw my label at the end of the line with 2 pixel offset
        super().draw(renderer)
        for side, label in self.text_labels.items():
            label.draw(renderer)


class Coupling(Line2D):
    """
    Coupling artist for showing couplings between levels.
    """

    def __str__(self):
        if self._start is None:
            return "Coupling()"
        else:
            return "Coupling((%g,%g)->(%g,%g))" % (*self._start, *self._stop)

    def __init__(self, start, stop,
                 arrowsize, arrowratio=1,
                 tail=False,
                 arrow_kw={},
                 label='', label_offset='center',
                 label_rot=False, label_flip=False,
                 label_kw={},
                 **kwargs
                 ):

        if not np.iterable(start) or not np.iterable(stop):
            raise RuntimeError('x/y data must be a sequence of two elements')
        elif len(start) != 2 or len(stop) != 2:
            raise RuntimeError('x/y data must be a sequence of two elements')

        start = np.array(start)
        stop = np.array(stop)

        self._start = start
        self._stop = stop
        self._lw = kwargs.get('linewidth',1)
        self._arrowsize = arrowsize
        self._arrowratio = arrowratio
        self._tail = tail
        self.tail = False

        x0, y0 = self.init_path()
        super().__init__(x0, y0, **kwargs)

        # initialize arrowheads
        # use line kwargs to set arrow defaults
        arrow_kw.update(kwargs)
        self.init_arrowheads(**arrow_kw)

        # initialize label text
        self.init_label(label, label_offset, label_rot, label_flip, **label_kw)

    def init_path(self):

        vec = self._stop - self._start
        dist = np.sqrt(vec.dot(vec))
        self._dist = dist
        self._ang = np.arctan2(*vec[::-1])
        if self._tail:
            x0, y0 = np.stack(((self._arrowsize,0),(dist - self._arrowsize,0))).T
        else:
            x0, y0 = np.stack(((0,0),(dist - self._arrowsize,0))).T

        return x0, y0

    def init_arrowheads(self, **kwargs):

        verts = np.array([[-1,0.5],[-1,-0.5],[0,0]])
        self.head = mpl.patches.Polygon(verts, closed=True, **kwargs)
        if self._tail:
            self.tail = mpl.patches.Polygon(verts, closed=True, **kwargs)

    def init_label(self, label, label_offset, label_rot, label_flip, **label_kw):

        if label_offset == 'center':
            label_ha = 'center'
            # define softbackground for text
            bbox_defaults = {'boxstyle':'round,pad=0.05','fc':'w','ec':'none','alpha':0.5}
            bbox_dict = label_kw.pop('bbox',{})
            bbox_dict = {**bbox_defaults, **bbox_dict}
            label_kw['bbox'] = bbox_dict
        # flip to match anchor ha settings
        elif label_offset == 'right':
            label_ha = 'left'
        elif label_offset == 'left':
            label_ha = 'right'
        self.text = mpl.text.Text(self._dist/2, 0, label, ha=label_ha, va='center',
                                  transform_rotates_text=label_rot, rotation=label_flip*180,
                                  **label_kw)
        # give space for non-centered text
        self.text_shift = np.array([0,0])
        if not label_rot:
            pad = self.text.get_fontsize()/2  # in points
        else:
            pad = 0
        if label_ha == 'left':
            self.text_shift[0] += pad
        elif label_ha == 'right':
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

        head_transform = affine().scale(self._arrowsize,
                                        self._arrowsize*self._arrowratio).rotate(self._ang).translate(*self._stop)
        self.head.set_transform(head_transform + transform)

        if self.tail:
            tail_transform = affine().scale(self._arrowsize,
                                            self._arrowsize*self._arrowratio).rotate(self._ang+np.pi).translate(*self._start)
            self.tail.set_transform(tail_transform + transform)

        # want to translate text shim in points
        text_shim = affine().translate(*self.text_shift)
        # want main translate in 'data' coords
        text_transform = affine().rotate(self._ang).translate(*self._start)
        self.text.set_transform(text_transform + transform + text_shim)

        # lw_shim = affine().scale(
        line_transform = affine().rotate(self._ang).translate(*self._start)
        super().set_transform(line_transform + transform)

    def set_data(self, x, y):

        super().set_data(x, y)

    def draw(self, renderer):

        super().draw(renderer)
        self.head.draw(renderer)
        if self.tail:
            self.tail.draw(renderer)
        self.text.draw(renderer)


class WavyCoupling(Coupling):
    """
    Coupling that uses a sine wave for the line.
    """

    def __str__(self):
        if self._start is None:
            return "WavyCoupling()"
        else:
            return "WavyCoupling((%g,%g)->(%g,%g))" % (*self._start, *self._stop)

    def __init__(self, start, stop,
                 waveamp, halfperiod, arrowsize, arrowratio=1,
                 tail=False,
                 arrow_kw={},
                 label='', label_offset='center',
                 label_rot=False, label_flip=False,
                 label_kw={},
                 **kwargs
                 ):

        self._waveamp = waveamp
        self._halfperiod = halfperiod

        if arrowsize*arrowratio < waveamp:
            warnings.warn('Wave amplitude is larger than arrowhead; result will look funny.')

        super().__init__(start, stop,
                         arrowsize, arrowratio,
                         tail,
                         arrow_kw,
                         label, label_offset,
                         label_rot, label_flip,
                         label_kw,
                         **kwargs)
        if not np.iterable(start) or not np.iterable(stop):
            raise RuntimeError('x/y data must be a sequence of two elements')
        elif len(start) != 2 or len(stop) != 2:
            raise RuntimeError('x/y data must be a sequence of two elements')

    def init_path(self):

        vec = self._stop - self._start
        dist = np.sqrt(vec.dot(vec))
        self._dist = dist
        self._ang = np.arctan2(*vec[::-1])

        omega = np.pi/self._halfperiod

        amp = self._waveamp/2
        phi = omega*self._arrowsize
        npoints = 151
        x0 = np.linspace(0, dist - self._arrowsize, npoints)
        y0 = amp*np.sin(omega*x0 + phi)

        return x0, y0
