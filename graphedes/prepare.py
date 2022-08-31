from dataclasses import dataclass
import html
from typing import Optional

import networkx as nx
import pydot as dt

from graphedes.convert import EdsNode, EdsNodeTy


@dataclass
class NxToDotConfig:
    use_node_ty_colors: bool = True
    font: Optional[str] = None


def label(graph: nx.DiGraph) -> nx.DiGraph:
    """
    Inject human readable labels to the EDS graph.

    Returns
    ---
    graph
        The graph modified inplace.
    """
    for handle in graph.nodes:
        node = graph.nodes[handle]
        meta: EdsNode = node["meta"]

        properties = [
            f'<tr><td sides="l" border="1" align="left">{html.escape(key)}</td><td sides="r" border="1" align="left">{html.escape(val)}</td></tr>'
            for key, val in meta.properties.items()
        ]

        node[
            "label"
        ] = f'<<table align="center" border="0" cellspacing="0"><tr><td colspan="2">{html.escape(meta.predicate)}</td></tr><tr><td colspan="2">{html.escape(f"<{meta.span[0]},{meta.span[1]}>")}</td></tr>{"".join(properties)}</table>>'

    for handle_u, handle_v in graph.edges:
        edge = graph.edges[handle_u, handle_v]
        meta = edge["meta"]
        edge["label"] = '"{}"'.format(html.escape(f"{meta.ty}"))

    return graph


def color(graph: nx.DiGraph) -> nx.DiGraph:
    for handle in graph.nodes:
        node = graph.nodes[handle]
        meta: EdsNode = node["meta"]

        if meta.ty == EdsNodeTy.E:
            node["color"] = "red"
        elif meta.ty == EdsNodeTy.X:
            node["color"] = "black"
        else:
            node["color"] = "blue"

    return graph


def clean(graph: nx.DiGraph) -> nx.DiGraph:
    for handle in graph.nodes:
        node = graph.nodes[handle]
        del node["meta"]
        if "_" in node:
            del node["_"]

    for handle_u, handle_v in graph.edges:
        edge = graph.edges[handle_u, handle_v]
        del edge["meta"]
        if "_" in edge:
            del edge["_"]

    return graph


def inject_default(graph: nx.DiGraph) -> nx.DiGraph:
    defaults = nx.DiGraph()
    defaults.add_node("node")
    defaults.add_node("edge")
    return nx.compose(defaults, graph)


def get_default_node(dot: dt.Dot) -> dt.Node:
    if (lst := dot.get_node("node")) and len(lst) != 0:
        return lst[0]
    else:
        node = dt.Node("node")
        dot.add_node(node)
        return node


def get_default_edge(dot: dt.Dot) -> dt.Node:
    if (lst := dot.get_node("edge")) and len(lst) != 0:
        return lst[0]
    else:
        node = dt.Node("edge")
        dot.add_node(node)
        return node


def stylize(dot: dt.Dot, *, font: Optional[str] = None) -> dt.Dot:
    if font is not None:
        get_default_node(dot).set("fontname", font)
        get_default_edge(dot).set("fontname", font)

    for node in dot.get_node_list():
        node: dt.Node
        # node.set("fontname", "JetBrains Mono")

        if (color := node.get("color")) is not None:
            node.set("fontcolor", color)

    # for edge in dot.get_edge_list():
    # edge: dt.Edge
    # edge.set("fontname", "JetBrains Mono")

    return dot


def nx_to_dot(graph: nx.DiGraph, config: NxToDotConfig = NxToDotConfig()) -> dt.Dot:
    graph = label(graph)

    if config.use_node_ty_colors:
        graph = color(graph)

    graph = inject_default(clean(graph))

    dot = nx.nx_pydot.to_pydot(graph)
    dot = stylize(dot, font=config.font)

    return dot
