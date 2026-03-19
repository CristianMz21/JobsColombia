from jobscolombia.utils import columnas_export, generar_nombre_csv


class TestGenerarNombreCsv:
    def test_filename_contains_prefix(self):
        filename = generar_nombre_csv()
        assert filename.startswith("comparativa_mercado_")

    def test_filename_contains_timestamp(self):
        import re

        filename = generar_nombre_csv()
        pattern = r"comparativa_mercado_\d{8}_\d{4}\.csv"
        assert re.match(pattern, filename) is not None

    def test_filename_ends_with_csv(self):
        filename = generar_nombre_csv()
        assert filename.endswith(".csv")


class TestColumnasExport:
    def test_returns_list(self):
        result = columnas_export()
        assert isinstance(result, list)

    def test_contains_required_columns(self):
        result = columnas_export()
        assert "score" in result
        assert "title" in result
        assert "company" in result
        assert "job_url" in result

    def test_is_ordered(self):
        result = columnas_export()
        assert result.index("score") < result.index("title")
