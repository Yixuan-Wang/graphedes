import sys
from enum import Enum
from pathlib import Path
from typing import Optional

import typer
from delphin.eds import EDS, from_mrs
from rich import print

from graphedes.convert import eds_to_nx
from graphedes.prepare import NxToDotConfig, nx_to_dot

app = typer.Typer()


class InputFormat(str, Enum):
    Mrs = "mrs"
    MrsJson = "mrs_json"
    Eds = "eds"
    EdsJson = "eds_json"
    AceOutput = "ace"


@app.command()
def sketch(
    path: Optional[Path] = typer.Argument(
        None, help="The path for input. Will read from stdin by default."
    ),
    input: Optional[str] = typer.Option(None, "-i", help="The input."),
    output: Optional[Path] = typer.Option(
        None, "-o", help="The path for output. Will write into stdout by default."
    ),
    format: InputFormat = typer.Option(InputFormat.Eds, "-f", help="The input format."),
    color: bool = typer.Option(
        False, help="Whether to use colors to discriminate different nodes."
    ),
    font: str = typer.Option("Courier New", help="The font used in the EDS graph."),
):
    """
    Convert the semantic representation to a paintable EDS graph in DOT format.
    """

    if input is None:
        if path is not None:
            input = path.read_text()
        else:
            with sys.stdin as stdin:
                input = stdin.read()

    eds_graph: EDS
    if format == InputFormat.AceOutput:
        from delphin.codecs import simplemrs

        input = input[input.find("\n") + 1 :]
        eds_graph = from_mrs(simplemrs.decode(input))
    elif format == InputFormat.Mrs:
        from delphin.codecs import simplemrs

        eds_graph = from_mrs(simplemrs.decode(input))
    elif format == InputFormat.MrsJson:
        from delphin.codecs import mrsjson

        eds_graph = from_mrs(mrsjson.decode(input))
    elif format == InputFormat.Eds:
        from delphin.codecs import eds

        eds_graph = eds.decode(input)
    elif format == InputFormat.EdsJson:
        from delphin.codecs import edsjson

        eds_graph = edsjson.decode(input)
    else:
        raise NotImplemented("Not a supported format.")

    graph = eds_to_nx(eds_graph)
    dot = nx_to_dot(graph, NxToDotConfig(use_node_ty_colors=color, font=font,))

    dot_str = dot.to_string()
    if output is not None:
        output.write_text(dot_str)
    else:
        with sys.stdout as f:
            f.write(dot_str)


@app.command()
def version():
    import pkg_resources

    version = pkg_resources.get_distribution("graphedes").version
    print(f"graphedes [blue bold]{version}[/]")
