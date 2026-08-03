"""Tests for the Parser class (src/parser/parser.py)."""

import os
import tempfile

import pytest

from src.parser.parser import Parser

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _tmp(content: str) -> str:
    """Write *content* to a temporary file and return its path."""
    f = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    )
    f.write(content)
    f.close()
    return f.name


# ---------------------------------------------------------------------------
# Happy‑path tests
# ---------------------------------------------------------------------------


class TestParserValid:
    def test_minimal_map(self) -> None:
        path = _tmp(
            "nb_drones: 1\nstart_hub: s 0 0\nend_hub: e 1 1\n"
            "connection: s-e\n"
        )
        config = Parser(path).parse()
        assert config["nb_drones"] == 1
        assert config["start_hub"]["name"] == "s"
        assert config["end_hub"]["name"] == "e"
        assert len(config["connection"]) == 1
        os.unlink(path)

    def test_nb_drones_large(self) -> None:
        path = _tmp(
            "nb_drones: 100\nstart_hub: s 0 0\nend_hub: e 1 1\n"
            "connection: s-e\n"
        )
        config = Parser(path).parse()
        assert config["nb_drones"] == 100
        os.unlink(path)

    def test_intermediate_hubs(self) -> None:
        path = _tmp(
            "nb_drones: 2\n"
            "start_hub: s 0 0\n"
            "hub: a 1 0\n"
            "hub: b 2 0\n"
            "end_hub: e 3 0\n"
            "connection: s-a\n"
            "connection: a-b\n"
            "connection: b-e\n"
        )
        config = Parser(path).parse()
        assert len(config["hub"]) == 2
        names = [h["name"] for h in config["hub"]]
        assert "a" in names and "b" in names
        os.unlink(path)

    def test_comments_are_ignored(self) -> None:
        path = _tmp(
            "# this is a comment\n"
            "nb_drones: 1\n"
            "# another comment\n"
            "start_hub: s 0 0\n"
            "end_hub: e 1 1\n"
            "connection: s-e\n"
        )
        config = Parser(path).parse()
        assert config["nb_drones"] == 1
        os.unlink(path)

    def test_blank_lines_ignored(self) -> None:
        path = _tmp(
            "nb_drones: 1\n\n"
            "start_hub: s 0 0\n\n"
            "end_hub: e 1 1\n"
            "connection: s-e\n"
        )
        config = Parser(path).parse()
        assert config["nb_drones"] == 1
        os.unlink(path)

    # --- Metadata ---

    def test_zone_type_normal(self) -> None:
        path = _tmp(
            "nb_drones: 1\n"
            "start_hub: s 0 0\n"
            "hub: x 1 0 [zone=normal]\n"
            "end_hub: e 2 0\n"
            "connection: s-x\nconnection: x-e\n"
        )
        config = Parser(path).parse()
        assert config["hub"][0]["metadata"]["zone"] == "normal"
        os.unlink(path)

    def test_zone_type_restricted(self) -> None:
        path = _tmp(
            "nb_drones: 1\n"
            "start_hub: s 0 0\n"
            "hub: x 1 0 [zone=restricted]\n"
            "end_hub: e 2 0\n"
            "connection: s-x\nconnection: x-e\n"
        )
        config = Parser(path).parse()
        assert config["hub"][0]["metadata"]["zone"] == "restricted"
        os.unlink(path)

    def test_zone_type_priority(self) -> None:
        path = _tmp(
            "nb_drones: 1\n"
            "start_hub: s 0 0\n"
            "hub: x 1 0 [zone=priority]\n"
            "end_hub: e 2 0\n"
            "connection: s-x\nconnection: x-e\n"
        )
        config = Parser(path).parse()
        assert config["hub"][0]["metadata"]["zone"] == "priority"
        os.unlink(path)

    def test_zone_type_blocked(self) -> None:
        path = _tmp(
            "nb_drones: 1\n"
            "start_hub: s 0 0\n"
            "hub: x 1 0 [zone=blocked]\n"
            "end_hub: e 2 0\n"
            "connection: s-x\nconnection: x-e\n"
        )
        config = Parser(path).parse()
        assert config["hub"][0]["metadata"]["zone"] == "blocked"
        os.unlink(path)

    def test_color_metadata(self) -> None:
        path = _tmp(
            "nb_drones: 1\n"
            "start_hub: s 0 0 [color=green]\n"
            "end_hub: e 1 1 [color=red]\n"
            "connection: s-e\n"
        )
        config = Parser(path).parse()
        assert config["start_hub"]["metadata"]["color"] == "green"
        assert config["end_hub"]["metadata"]["color"] == "red"
        os.unlink(path)

    def test_max_drones_on_hub(self) -> None:
        path = _tmp(
            "nb_drones: 1\n"
            "start_hub: s 0 0\n"
            "hub: x 1 0 [max_drones=3]\n"
            "end_hub: e 2 0\n"
            "connection: s-x\nconnection: x-e\n"
        )
        config = Parser(path).parse()
        assert config["hub"][0]["metadata"]["max_drones"] == 3
        os.unlink(path)

    def test_max_link_capacity(self) -> None:
        path = _tmp(
            "nb_drones: 2\n"
            "start_hub: s 0 0\n"
            "end_hub: e 1 1\n"
            "connection: s-e [max_link_capacity=4]\n"
        )
        config = Parser(path).parse()
        assert config["connection"][0][2]["max_link_capacity"] == 4
        os.unlink(path)

    def test_mixed_metadata_on_hub(self) -> None:
        path = _tmp(
            "nb_drones: 1\n"
            "start_hub: s 0 0\n"
            "hub: x 1 0 [zone=priority color=blue max_drones=2]\n"
            "end_hub: e 2 0\n"
            "connection: s-x\nconnection: x-e\n"
        )
        config = Parser(path).parse()
        meta = config["hub"][0]["metadata"]
        assert meta["zone"] == "priority"
        assert meta["color"] == "blue"
        assert meta["max_drones"] == 2
        os.unlink(path)

    def test_max_drones_on_start_end_is_not_an_error(self) -> None:
        """max_drones on start/end is silently accepted (
            overridden to nb_drones)."""
        path = _tmp(
            "nb_drones: 3\n"
            "start_hub: s 0 0 [max_drones=1]\n"
            "end_hub: e 1 1 [max_drones=1]\n"
            "connection: s-e\n"
        )
        # Must NOT raise
        config = Parser(path).parse()
        assert config["nb_drones"] == 3
        os.unlink(path)

    def test_coordinates_stored_correctly(self) -> None:
        path = _tmp(
            "nb_drones: 1\n"
            "start_hub: s 3 7\n"
            "end_hub: e 10 20\n"
            "connection: s-e\n"
        )
        config = Parser(path).parse()
        assert config["start_hub"]["coordinate"] == (3, 7)
        assert config["end_hub"]["coordinate"] == (10, 20)
        os.unlink(path)

    def test_connection_stores_both_zone_names(self) -> None:
        path = _tmp(
            "nb_drones: 1\n"
            "start_hub: alpha 0 0\n"
            "end_hub: beta 1 1\n"
            "connection: alpha-beta\n"
        )
        config = Parser(path).parse()
        c = config["connection"][0]
        assert c[0] == "alpha"
        assert c[1] == "beta"
        os.unlink(path)


# ---------------------------------------------------------------------------
# Error tests — nb_drones
# ---------------------------------------------------------------------------


class TestParserNbDronesErrors:
    def test_nb_drones_missing(self) -> None:
        path = _tmp("start_hub: s 0 0\nend_hub: e 1 1\n")
        with pytest.raises(ValueError, match="nb_drones"):
            Parser(path).parse()
        os.unlink(path)

    def test_nb_drones_zero(self) -> None:
        path = _tmp("nb_drones: 0\nstart_hub: s 0 0\nend_hub: e 1 1\n")
        with pytest.raises(ValueError):
            Parser(path).parse()
        os.unlink(path)

    def test_nb_drones_negative(self) -> None:
        path = _tmp("nb_drones: -1\nstart_hub: s 0 0\nend_hub: e 1 1\n")
        with pytest.raises(ValueError):
            Parser(path).parse()
        os.unlink(path)

    def test_nb_drones_float(self) -> None:
        path = _tmp("nb_drones: 1.5\nstart_hub: s 0 0\nend_hub: e 1 1\n")
        with pytest.raises(ValueError):
            Parser(path).parse()
        os.unlink(path)

    def test_nb_drones_not_first(self) -> None:
        path = _tmp("start_hub: s 0 0\nnb_drones: 1\nend_hub: e 1 1\n")
        with pytest.raises(ValueError, match="nb_drones"):
            Parser(path).parse()
        os.unlink(path)


# ---------------------------------------------------------------------------
# Error tests — hubs
# ---------------------------------------------------------------------------


class TestParserHubErrors:
    def test_missing_start_hub(self) -> None:
        path = _tmp("nb_drones: 1\nend_hub: e 1 1\n")
        with pytest.raises(ValueError):
            Parser(path).parse()
        os.unlink(path)

    def test_missing_end_hub(self) -> None:
        path = _tmp("nb_drones: 1\nstart_hub: s 0 0\n")
        with pytest.raises(ValueError):
            Parser(path).parse()
        os.unlink(path)

    def test_duplicate_start_hub(self) -> None:
        path = _tmp(
            "nb_drones: 1\n"
            "start_hub: s 0 0\n"
            "start_hub: s2 1 1\n"
            "end_hub: e 2 2\n"
        )
        with pytest.raises(ValueError, match="duplicate"):
            Parser(path).parse()
        os.unlink(path)

    def test_duplicate_hub_name(self) -> None:
        path = _tmp(
            "nb_drones: 1\n"
            "start_hub: a 0 0\n"
            "hub: a 1 1\n"
            "end_hub: b 2 2\n"
        )
        with pytest.raises(ValueError, match="[Dd]uplicate"):
            Parser(path).parse()
        os.unlink(path)

    def test_dash_in_zone_name(self) -> None:
        path = _tmp("nb_drones: 1\n" "start_hub: a-b 0 0\n" "end_hub: c 1 1\n")
        with pytest.raises(ValueError, match="dash"):
            Parser(path).parse()
        os.unlink(path)

    def test_invalid_zone_type(self) -> None:
        path = _tmp(
            "nb_drones: 1\n"
            "start_hub: s 0 0\n"
            "hub: x 1 0 [zone=unknown]\n"
            "end_hub: e 2 0\n"
            "connection: s-x\nconnection: x-e\n"
        )
        with pytest.raises(ValueError, match="[Zz]one"):
            Parser(path).parse()
        os.unlink(path)

    def test_max_drones_zero_on_hub(self) -> None:
        path = _tmp(
            "nb_drones: 1\n"
            "start_hub: s 0 0\n"
            "hub: x 1 0 [max_drones=0]\n"
            "end_hub: e 2 0\n"
            "connection: s-x\nconnection: x-e\n"
        )
        with pytest.raises(ValueError):
            Parser(path).parse()
        os.unlink(path)

    def test_unknown_metadata_key_on_hub(self) -> None:
        path = _tmp(
            "nb_drones: 1\n"
            "start_hub: s 0 0\n"
            "hub: x 1 0 [speed=fast]\n"
            "end_hub: e 2 0\n"
        )
        with pytest.raises(ValueError):
            Parser(path).parse()
        os.unlink(path)


# ---------------------------------------------------------------------------
# Error tests — connections
# ---------------------------------------------------------------------------


class TestParserConnectionErrors:
    def test_duplicate_connection_ab(self) -> None:
        path = _tmp(
            "nb_drones: 1\n"
            "start_hub: a 0 0\n"
            "end_hub: b 1 1\n"
            "connection: a-b\n"
            "connection: a-b\n"
        )
        with pytest.raises(ValueError, match="[Dd]uplicate"):
            Parser(path).parse()
        os.unlink(path)

    def test_duplicate_connection_ba(self) -> None:
        """b-a is a duplicate of a-b."""
        path = _tmp(
            "nb_drones: 1\n"
            "start_hub: a 0 0\n"
            "end_hub: b 1 1\n"
            "connection: a-b\n"
            "connection: b-a\n"
        )
        with pytest.raises(ValueError, match="[Dd]uplicate"):
            Parser(path).parse()
        os.unlink(path)

    def test_connection_unknown_zone(self) -> None:
        path = _tmp(
            "nb_drones: 1\n"
            "start_hub: a 0 0\n"
            "end_hub: b 1 1\n"
            "connection: a-c\n"
        )
        with pytest.raises(ValueError, match="[Uu]ndefined|[Uu]nknown"):
            Parser(path).parse()
        os.unlink(path)

    def test_max_link_capacity_zero(self) -> None:
        path = _tmp(
            "nb_drones: 1\n"
            "start_hub: a 0 0\n"
            "end_hub: b 1 1\n"
            "connection: a-b [max_link_capacity=0]\n"
        )
        with pytest.raises(ValueError):
            Parser(path).parse()
        os.unlink(path)

    def test_unknown_connection_metadata_key(self) -> None:
        path = _tmp(
            "nb_drones: 1\n"
            "start_hub: a 0 0\n"
            "end_hub: b 1 1\n"
            "connection: a-b [weight=5]\n"
        )
        with pytest.raises(ValueError):
            Parser(path).parse()
        os.unlink(path)


# ---------------------------------------------------------------------------
# Error tests — file I/O
# ---------------------------------------------------------------------------


class TestParserIOErrors:
    def test_file_not_found(self) -> None:
        with pytest.raises(FileNotFoundError):
            Parser("/nonexistent/path/map.txt").parse()

    def test_unrecognized_line_format(self) -> None:
        path = _tmp(
            "nb_drones: 1\n"
            "start_hub: s 0 0\n"
            "end_hub: e 1 1\n"
            "garbage line here\n"
        )
        with pytest.raises(ValueError):
            Parser(path).parse()
        os.unlink(path)
