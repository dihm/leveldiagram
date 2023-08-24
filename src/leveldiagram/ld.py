"""
Base Level Diagram class
"""

import matplotlib.pyplot as plt

from typing import Dict, Tuple, Optional, Literal, Any
from networkx import DiGraph
from matplotlib.axes import Axes

from .utils import deep_update, ket_str
from .artists import EnergyLevel, Coupling, WavyCoupling


class LD:
    """
    Basic Level Diagram drawing class.

    This class is used to draw a level diagram based on a provided Directional Graph.
    The nodes of this graph define the energy levels, the edges define the couplings.
    """

    _level_defaults = {"width": 1, "color": "k", "text_kw": {"fontsize": "large"}}
    "EnergyLevel default parameters dictionary"

    _coupling_defaults = {"arrowsize": 0.15, "label_kw": {"fontsize": "large"}}
    "Coupling default parameters dictionary"

    _wavycoupling_defaults = {"waveamp": 0.1, "halfperiod": 0.1}
    "WavyCoupling default parameters dictionary"

    def __init__(
        self,
        graph: DiGraph,
        ax: Optional[Axes] = None,
        default_label: Literal[
            "none", "left_text", "right_text", "top_text", "bottom_text"
        ] = "left_text",
        level_defaults: Optional[Dict[str, Any]] = None,
        coupling_defaults: Optional[Dict[str, Any]] = None,
        wavycoupling_defaults: Optional[Dict[str, Any]] = None,
    ):
        """
        Parameters:
            graph (networkx.DiGraph): Graph object that defines the system to diagram
            ax (matplotlib.axes.Axes, optional): Axes to add the diagram to. If None, creates a new figure and axes.
                Default is None.
            default_label (str, optional): Sets which text label direction to use for default labelling,
                which is the node index inside a key.
                Valid options are `'left_text'`, `'right_text'`, `'top_text'`, `'bottom_text'`.
                If 'none', no default labels are not generated.
            level_defaults (dict, optional): :class:`~.EnergyLevel` default values for whole diagram.
                Provided values override class defaults.
                If None, use class defaults.
            coupling_defaults (dict, optional): :class:`~.Coupling` default values for whole diagram.
                Provided values override class defaults.
                If None, use class defaults.
            wavycoupling_defaults (dict, optional): :class:`~.WavyCoupling` default values for whole diagram.
                Provided values override class defaults.
                If None, use class defaults.

        In keeping with the finest matplotlib traditions,
        default options and behavior will produce a *reasonable* output from a graph.

        Examples:
            >>> nodes = (0,1,2)
            >>> edges = ((0,1), (1,2))
            >>> graph = nx.DiGraph()
            >>> graph.add_nodes_from(nodes)
            >>> graph.add_edges_from(edges)
            >>> d = ld.LD(graph)
            >>> d.draw()

            .. image:: basic_example.png
              :width: 400
              :alt: Basic 3-level diagram with 2 couplings using all default settings

        To get more refined diagrams, global options can be set by passing keyword argument
        dictionaries to the constructor.
        Options per level or coupling can be set by setting keyword arguments in the dictionaries
        of the nodes and edges of the graph.
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

        if wavycoupling_defaults is None:
            self.wavycoupling_defaults = self._wavycoupling_defaults
        else:
            self.wavycoupling_defaults = deep_update(
                self._wavycoupling_defaults, wavycoupling_defaults
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

        for n in self._graph.nodes:
            node = self._graph.nodes[n].copy()
            # if x,y coords not defined, set using node index
            node.setdefault("energy", n)
            node.setdefault("xpos", n)

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
            edge = self._graph.edges[ed].copy()
            # set default options
            edge = deep_update(self.coupling_defaults, edge)
            # pop off non-arguments
            det = edge.pop("detuning", 0)
            anchor = edge.pop("anchor", "center")
            # set where couplings join the levels
            start = self.levels[ed[0]].get_anchor(anchor)
            stop = self.levels[ed[1]].get_anchor(anchor)
            # adjust for detuning
            stop[1] -= det
            edge.setdefault("start", start)
            edge.setdefault("stop", stop)
            # auto-cycle colors
            if "color" not in edge:
                edge["color"] = self.ax._get_lines.get_next_color()

            if edge.pop("wavy", False):
                edge.update(self.wavycoupling_defaults)
                self.couplings[ed] = WavyCoupling(**edge)
            else:
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
