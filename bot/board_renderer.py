import io
import chess
import chess.svg
import cairosvg


def render_board_png(fen: str, size: int = 400, flipped: bool = False) -> bytes:
    """
    Render a chess board from FEN position to PNG bytes.

    Args:
        fen: FEN string representing the position
        size: Size of the output image in pixels
        flipped: Whether to flip the board (black's perspective)

    Returns:
        PNG image as bytes
    """
    board = chess.Board(fen)

    # Generate SVG
    svg_data = chess.svg.board(
        board,
        size=size,
        flipped=flipped,
        colors={
            "square light": "#ebecd0",
            "square dark": "#779556",
        },
    )

    # Convert SVG to PNG
    png_data = cairosvg.svg2png(bytestring=svg_data.encode("utf-8"))

    return png_data


def get_board_file(fen: str, flipped: bool = False) -> io.BytesIO:
    """
    Get a chess board image as a file-like object for Discord.

    Args:
        fen: FEN string representing the position
        flipped: Whether to flip the board

    Returns:
        BytesIO object containing PNG image
    """
    png_data = render_board_png(fen, size=400, flipped=flipped)
    return io.BytesIO(png_data)
