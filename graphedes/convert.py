from __future__ import annotations

import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, cast

if sys.version_info > (3, 10):
    from typing import Self
else:
    from typing_extensions import Self

import delphin.eds as di_eds
import networkx as nx


@dataclass
class EdsNode:
    # _: Optional[di_eds.Node]
    # """The original `delphin.eds.Node` object. Can be erased for serialization reasons."""

    predicate: str
    """The predicate of this EDS node."""

    span: tuple[int, int]
    """The range of this sentence in the original sentence. Inclusive at the beginning, exclusive on the end."""

    properties: dict[str, str]
    """The properties of this EDS node. Guaranteed to be non-null."""

    constant: Optional[str]
    """The constant value of this EDS node."""

    ty: EdsNodeTy
    """The type of this EDS node."""


class EdsNodeTy(str, Enum):
    X = "x"
    """Variable"""

    E = "e"
    """Event"""

    Q = "q"
    """Quantifier"""


@dataclass
class EdsEdge:
    ty: EdsEdgeTy
    """The type of this EDS edge."""


class EdsEdgeTy(int):
    BV = 0
    L_INDEX = -1
    R_INDEX = -2

    def __new__(cls: type[Self], val: Any) -> Self:
        if isinstance(val, str):
            if val == "BV":
                val = 0
            elif val == "L-INDEX":
                val = -1
            elif val == "R-INDEX":
                val = -2
            elif val.startswith("ARG"):
                val = int(val[3:])
            else:
                val = int(val)

        return super().__new__(cls, val)

    def __repr__(self) -> str:
        if self == 0:
            return "BV"
        elif self == -1:
            return "L-INDEX"
        elif self == -2:
            return "R-INDEX"
        else:
            return f"ARG{super().__repr__()}"

    def __str__(self) -> str:
        return self.__repr__()


@dataclass
class EdsToNxConfig:
    include_delphin_node: bool = False


def eds_to_nx(eds: di_eds.EDS, config: EdsToNxConfig = EdsToNxConfig()) -> nx.DiGraph:
    """
    Convert a `delphin.eds.EDS` structure to a `networkx.DiGraph`. You can assume that the node will be represented by the EDS node id in DELPH-IN style, and the metadata of the nodes and edges will be `EdsNode` and `EdsEdge`, respectively.


    Returns
    ---
    result
        The equivalent `DiGraph`.
    """
    graph = nx.DiGraph()

    for di_node in eds.nodes:
        di_node = cast(di_eds.Node, di_node)
        graph.add_node(
            di_node.id,
            meta=EdsNode(
                predicate=di_node.predicate,
                span=(di_node.cfrom, di_node.cto),
                constant=di_node.carg,
                properties=di_node.properties if di_node.properties is not None else {},
                ty=EdsNodeTy(ty if (ty := di_node.type) is not None else "q"),
            ),
        )
        if config.include_delphin_node:
            graph.nodes[di_node.id]["_"] = di_node

    for lhs_id, ty_str, rhs_id in eds.edges:
        ty = EdsEdgeTy(ty_str)
        graph.add_edge(lhs_id, rhs_id, meta=EdsEdge(ty=ty))

    return graph
