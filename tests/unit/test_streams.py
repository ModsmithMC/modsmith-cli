import io

from modsmith_app.cli.app import tolerate_unencodable


def test_unencodable_characters_become_question_marks():
    raw = io.BytesIO()
    stream = io.TextIOWrapper(raw, encoding="gbk")

    tolerate_unencodable(stream, io.StringIO())
    stream.write("Sodium \U0001f680 中文 …")
    stream.flush()

    assert raw.getvalue().decode("gbk") == "Sodium ? 中文 …"
