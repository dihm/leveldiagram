"""
Base Level Diagram class
"""

import matplotlib.pyplot as plt

from typing import Dict, Tuple, Optional, Literal, Any
from networkx import DiGraph
from matplotlib.axes import Axes

from .utils import deep_update, ket_str
from .artists import EnergyLevel, Coupling


class LD:
    """
    Basic Level Diagram drawing class.

    This class is used to draw a level diagram based on a provided Directional Graph.
    The nodes of this graph define the energy levels, the edges define the couplings.

    Note
    ----

    In keeping with the finest matplotlib traditions,
    default options and behavior will produce a *reasonable* output from a graph.
    To get more refined diagrams,
    global options can be set by passing keyword argument
    dictionaries to the constructor.
    Options per level or coupling can be set by setting keyword arguments
    in the dictionaries of the nodes and edges of the graph.

    Examples
    --------
    >>> nodes = (0,1,2)
    >>> edges = ((0,1), (1,2))
    >>> graph = nx.DiGraph()
    >>> graph.add_nodes_from(nodes)
    >>> graph.add_edges_from(edges)
    >>> d = ld.LD(graph)
    >>> d.draw()

    .. image:: img/basic_example.png
        :width: 400
        :alt: Basic 3-level diagram with 2 couplings using all default settings
    """

    _level_defaults = {"width": 1, "color": "k", "text_kw": {"fontsize": "large"}}
    "EnergyLevel default parameters dictionary"

    _coupling_defaults = {"arrowsize": 0.15, "label_kw": {"fontsize": "large"}}
    "Coupling default parameters dictionary"

    _wavy_defaults = {"waveamp": 0.05, "halfperiod": 0.1}
    "Default parameters for a wavy coupling"

    _deflection_defaults = {"deflection": 0.25}
    "Default parameters for a deflection"

    def __init__(
        self,
        graph: DiGraph,
        ax: Optional[Axes] = None,
        default_label: Literal[
            "none", "left_text", "right_text", "top_text", "bottom_text"
        ] = "left_text",
        level_defaults: Optional[Dict[str, Any]] = None,
        coupling_defaults: Optional[Dict[str, Any]] = None,
        wavy_defaults: Optional[Dict[str, Any]] = None,
        deflection_defaults: Optional[Dict[str, Any]] = None,
        use_ld_kw: bool = False,
    ):
        """
        Parameters
        ----------
        graph: networkx.DiGraph
            Graph object that defines the system to diagram

            Beyond the arguments provided to the :class:`Coupling` artist primitive,
            each coupling plotted by :class:`LD` can also take the following parameters
            (which are defined as edge attributes on the graph).

            - **hidden**: bool -
              Tells :class:`LD` to ignore this coupling
            - **start_anchor**: str or 2-element tuple -
              Controls the start anchor point
            - **stop_anchor**: str or 2-element tuple -
              Controls the stop anchor point
            - **detuning**: float -
              How much to detune the coupling from the transition by.
              Defined in x-coordinate units.
            - **wavy**: bool -
              Make coupling arrow a sine wave.
              Uses default options if wavy specific options not provided.
            - **deflect**: bool -
              Make coupling a deflected, circular coupling.
              Uses default options if deflect specific options not provided.

        ax: matplotlib.axes.Axes, optional
            Axes to add the diagram to.
            If None, creates a new figure and axes.
            Default is None.
        default_label: str, optional
            Sets which text label direction to use for default labelling,
            which is the node index inside a key.
            Valid options are `'left_text'`, `'right_text'`,
            `'top_text'`, `'bottom_text'`.
            If 'none', no default labels are not generated.
        level_defaults: dict, optional
            :class:`~.EnergyLevel` default values for whole diagram.
            Provided values override class defaults.
            If None, use class defaults.
        coupling_defaults: dict, optional
            :class:`~.Coupling` default values
            for whole diagram.
            Provided values override class defaults.
            If None, use class defaults.
        wavy_defaults: dict, optional
            Wavy specific :class:`~.Coupling` default values for whole diagram.
            Provided values override class defaults.
            If None, use class defaults.
        deflection_defaults: dict, optional
            Deflection specific :class:`~.Coupling` default values for whole diagram.
            Provided values override class defaults.
            If None, use class defaults.
        """

        if ax is None:
            _, ax = plt.subplots(1)
            ax.set_aspect("equal")
        self.fig = ax.get_figure()
        self.ax = ax

        self.ax.set_axis_off()

        self._graph = graph

        # control parameters
        self.default_label = default_label
        self.use_ld_kw = use_ld_kw

        # save default options for artists
        if level_defaults is None:
            self.level_defaults = self._level_defaults
        else:
            self.level_defaults = deep_update(self._level_defaults, level_defaults)

        if coupling_defaults is None:
            self.coupling_defaults = self._coupling_defaults
        else:
            self.coupling_defaults = deep_update(
                self._coupling_defaults, coupling_defaults
            )

        if wavy_defaults is None:
            self.wavy_defaults = self._wavy_defaults
        else:
            self.wavy_defaults = deep_update(
                self._wavy_defaults, wavy_defaults
            )

        if deflection_defaults is None:
            self.deflection_defaults = self._deflection_defaults
        else:
            self.deflection_defaults = deep_update(
                self._deflection_defaults, deflection_defaults
            )

        # internal storage objects
        self.levels: Dict[int, EnergyLevel] = {}
        """Stores levels to be drawn"""
        self.couplings: Dict[Tuple[int, int], Coupling] = {}
        """Stores couplings to be drawn"""

    def generate_levels(self):
        """
        Creates the EnergyLevel artists from the graph nodes.

        They are saved to the :attr:`levels` dictionary.
        """

        for i, n in enumerate(self._graph.nodes):
            if self.use_ld_kw:
                node = self._graph.nodes[n].get('ld_kw', {}).copy()
            else:
                node = self._graph.nodes[n].copy()
            # if x,y coords not defined, set using node index
            node.setdefault("energy", i)
            node.setdefault("xpos", i)

            if self.default_label != "none":
                node.setdefault(self.default_label, ket_str(n))

            # set default options
            node = deep_update(self.level_defaults, node)
            self.levels[n] = EnergyLevel(**node)

    def generate_couplings(self):
        """
        Creates the Coupling and WavyCoupling artisits from the graph edges.

        They are saved to the :attr:`couplings` dictionary.
        """

        for ed in self._graph.edges:
            if self.use_ld_kw:
                edge = self._graph.edges[ed].get("ld_kw", {}).copy()
            else:
                edge = self._graph.edges[ed].copy()
            # skip if hidden
            if edge.pop("hidden", False):
                continue
            # set default options
            edge = deep_update(self.coupling_defaults, edge)
            # pop off non-arguments
            det = edge.pop("detuning", 0)
            start_anchor = edge.pop("start_anchor", "center")
            stop_anchor = edge.pop("stop_anchor", "center")
            # set where couplings join the levels
            start = self.levels[ed[0]].get_anchor(start_anchor)
            stop = self.levels[ed[1]].get_anchor(stop_anchor)
            # adjust for detuning
            stop[1] -= det
            edge.setdefault("start", start)
            edge.setdefault("stop", stop)
            # auto-cycle colors
            if "color" not in edge:
                edge["color"] = self.ax._get_lines.get_next_color()

            wavy = edge.pop("wavy", False)
            deflect = edge.pop("deflect", False)
            if wavy:
                edge = deep_update(self.wavy_defaults, edge)
            if deflect:
                edge = deep_update(self.deflection_defaults, edge)
                
            self.couplings[ed] = Coupling(**edge)

    def draw(self):
        """
        Add artists to the figure.

        This calls :meth:`matplotlib:matplotlib.axes.Axes.autoscale_view` to ensure
        plot ranges are increased to account for objects.

        It may be necessary to increase plot margins to handle
        labels near edges of the plot.
        """

        self.generate_levels()
        self.generate_couplings()

        for lev in self.levels.values():
            self.ax.add_line(lev)
            for _, text in lev.text_labels.items():
                # registers text labels as artists on the axes
                # ensures text doesn't get clipped by figure edges
                self.ax._add_text(text)

        for coupling in self.couplings.values():
            self.ax.add_line(coupling)

        self.ax.autoscale_view()
