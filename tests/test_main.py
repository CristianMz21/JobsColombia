"""Tests for main module functions."""

import os
from unittest.mock import MagicMock, patch

import pandas as pd


class TestEnrichJobspyDataframe:
    """Test suite for _enrich_jobspy_dataframe function."""

    def test_enrich_adds_search_term_column(self):
        """_enrich_jobspy_dataframe should add search_term column."""
        # Import the function directly to avoid jobspy import at module level
        import sys
        sys.modules['jobspy'] = MagicMock()

        # Now we can import main
        with patch.dict('sys.modules', {'jobspy': MagicMock()}):
            # Need to reimport to pick up the mock
            import importlib

            import main
            importlib.reload(main)

            df = pd.DataFrame({
                "title": ["Python Developer"],
                "company": ["Tech Corp"],
                "job_url": ["https://linkedin.com/job/123"],
                "description": ["Python Django AWS"],
                "location": ["Bogotá"],
            })

            result = main._enrich_jobspy_dataframe(df, "Python")

            assert "search_term" in result.columns
            assert result["search_term"].iloc[0] == "Python"

    def test_enrich_adds_site_column(self):
        """_enrich_jobspy_dataframe should correctly identify site from URL."""
        with patch.dict('sys.modules', {'jobspy': MagicMock()}):
            import importlib

            import main
            importlib.reload(main)

            df = pd.DataFrame({
                "title": ["Python Developer"],
                "company": ["Tech Corp"],
                "job_url": ["https://linkedin.com/job/123"],
                "description": ["Python"],
                "location": ["Bogotá"],
            })

            result = main._enrich_jobspy_dataframe(df, "Python")

            assert "site" in result.columns
            assert result["site"].iloc[0] == "linkedin"

    def test_enrich_identifies_indeed_from_url(self):
        """_enrich_jobspy_dataframe should identify indeed from URL."""
        with patch.dict('sys.modules', {'jobspy': MagicMock()}):
            import importlib

            import main
            importlib.reload(main)

            df = pd.DataFrame({
                "title": ["Python Developer"],
                "company": ["Tech Corp"],
                "job_url": ["https://indeed.com/job/456"],
                "description": ["Python"],
                "location": ["Bogotá"],
            })

            result = main._enrich_jobspy_dataframe(df, "Python")

            assert result["site"].iloc[0] == "indeed"

    def test_enrich_adds_detected_technologies(self):
        """_enrich_jobspy_dataframe should add detected_technologies column."""
        with patch.dict('sys.modules', {'jobspy': MagicMock()}):
            import importlib

            import main
            importlib.reload(main)

            df = pd.DataFrame({
                "title": ["Python Developer"],
                "company": ["Tech Corp"],
                "job_url": ["https://linkedin.com/job/123"],
                "description": ["Python Django PostgreSQL"],
                "location": ["Bogotá"],
            })

            result = main._enrich_jobspy_dataframe(df, "Python")

            assert "detected_technologies" in result.columns
            assert "python" in result["detected_technologies"].iloc[0].lower()

    def test_enrich_adds_score_column(self):
        """_enrich_jobspy_dataframe should calculate and add score column."""
        with patch.dict('sys.modules', {'jobspy': MagicMock()}):
            import importlib

            import main
            importlib.reload(main)

            df = pd.DataFrame({
                "title": ["Python Developer"],
                "company": ["Tech Corp"],
                "job_url": ["https://linkedin.com/job/123"],
                "description": ["Python Django AWS Docker"],
                "location": ["Remoto"],
            })

            result = main._enrich_jobspy_dataframe(df, "Python")

            assert "score" in result.columns
            assert result["score"].iloc[0] > 0

    def test_enrich_adds_clasificacion_column(self):
        """_enrich_jobspy_dataframe should add clasificacion column."""
        with patch.dict('sys.modules', {'jobspy': MagicMock()}):
            import importlib

            import main
            importlib.reload(main)

            df = pd.DataFrame({
                "title": ["Python Developer"],
                "company": ["Tech Corp"],
                "job_url": ["https://linkedin.com/job/123"],
                "description": ["Python Django AWS Docker"],
                "location": ["Remoto"],
            })

            result = main._enrich_jobspy_dataframe(df, "Python")

            assert "clasificacion" in result.columns
            assert result["clasificacion"].iloc[0] in [
                "Excelente", "Buena", "Regular", "Descartada"
            ]

    def test_enrich_adds_stack_principal_column(self):
        """_enrich_jobspy_dataframe should add stack_principal column."""
        with patch.dict('sys.modules', {'jobspy': MagicMock()}):
            import importlib

            import main
            importlib.reload(main)

            df = pd.DataFrame({
                "title": ["Python Developer"],
                "company": ["Tech Corp"],
                "job_url": ["https://linkedin.com/job/123"],
                "description": ["Python Django"],
                "location": ["Bogotá"],
            })

            result = main._enrich_jobspy_dataframe(df, "Python")

            assert "stack_principal" in result.columns

    def test_enrich_does_not_modify_original_dataframe(self):
        """_enrich_jobspy_dataframe should not modify the original DataFrame."""
        with patch.dict('sys.modules', {'jobspy': MagicMock()}):
            import importlib

            import main
            importlib.reload(main)

            df = pd.DataFrame({
                "title": ["Python Developer"],
                "company": ["Tech Corp"],
                "job_url": ["https://linkedin.com/job/123"],
                "description": ["Python"],
                "location": ["Bogotá"],
            })

            original_columns = list(df.columns)

            main._enrich_jobspy_dataframe(df, "Python")

            assert list(df.columns) == original_columns


class TestPrintStatistics:
    """Test suite for print_statistics function."""

    def test_print_statistics_does_not_raise(self):
        """print_statistics should handle valid DataFrames without raising."""
        # print_statistics only uses logging, no imports needed
        from main import print_statistics

        df = pd.DataFrame({
            "title": ["Python Developer", "Java Developer"],
            "company": ["Tech Corp", "Tech Corp"],
            "site": ["linkedin", "indeed"],
            "stack_principal": ["Python/Django", "Java/Spring"],
            "clasificacion": ["Excelente", "Buena"],
            "score": [85, 70],
        })

        # Should not raise any exception
        print_statistics(df)

    def test_print_statistics_handles_empty_dataframe(self):
        """print_statistics should handle empty DataFrames."""
        from main import print_statistics

        df = pd.DataFrame({
            "title": [],
            "company": [],
            "site": [],
            "stack_principal": [],
            "clasificacion": [],
            "score": [],
        })

        # Should not raise
        print_statistics(df)

    def test_print_statistics_handles_missing_columns(self):
        """print_statistics should handle DataFrames with missing columns."""
        from main import print_statistics

        df = pd.DataFrame({
            "title": ["Python Developer"],
        })

        # Should not raise even with missing columns
        print_statistics(df)


class TestExportToCsv:
    """Test suite for export_to_csv function."""

    def test_export_to_csv_returns_string_path(self):
        """export_to_csv should return a string path."""
        from main import export_to_csv

        df = pd.DataFrame({
            "title": ["Python Developer"],
            "company": ["Tech Corp"],
            "site": ["linkedin"],
            "score": [85],
            "clasificacion": ["Excelente"],
            "stack_principal": ["Python/Django"],
            "job_url": ["https://example.com/job/1"],
            "location": ["Bogotá"],
            "description": [""],
            "detected_technologies": ["Python"],
            "search_term": ["Python"],
            "salary": [""],
            "date_posted": [""],
            "full_description": ["Python Django description"],
        })

        result = export_to_csv(df)

        assert isinstance(result, str)
        assert result.endswith(".csv")

    def test_export_to_csv_creates_file(self):
        """export_to_csv should create a CSV file."""
        from main import export_to_csv

        df = pd.DataFrame({
            "title": ["Python Developer"],
            "company": ["Tech Corp"],
            "site": ["linkedin"],
            "score": [85],
            "clasificacion": ["Excelente"],
            "stack_principal": ["Python/Django"],
            "job_url": ["https://example.com/job/1"],
            "location": ["Bogotá"],
            "description": [""],
            "detected_technologies": ["Python"],
            "search_term": ["Python"],
            "salary": [""],
            "date_posted": [""],
            "full_description": ["Python Django description"],
        })

        result = export_to_csv(df)

        assert os.path.exists(result)

        # Cleanup
        os.remove(result)

    def test_export_to_csv_respects_csv_columns(self):
        """export_to_csv should only export columns in CSV_COLUMNS."""
        from main import export_to_csv

        df = pd.DataFrame({
            "title": ["Python Developer"],
            "company": ["Tech Corp"],
            "site": ["linkedin"],
            "score": [85],
            "clasificacion": ["Excelente"],
            "stack_principal": ["Python/Django"],
            "job_url": ["https://example.com/job/1"],
            "location": ["Bogotá"],
            "description": [""],
            "detected_technologies": ["Python"],
            "search_term": ["Python"],
            "salary": [""],
            "date_posted": [""],
            "full_description": ["Python Django description"],
            "extra_column": ["should not appear"],
        })

        result = export_to_csv(df)

        df_read = pd.read_csv(result)
        assert "extra_column" not in df_read.columns

        # Cleanup
        os.remove(result)

    def test_export_to_csv_with_custom_filename(self):
        """export_to_csv should use custom filename when provided."""
        from main import export_to_csv

        df = pd.DataFrame({
            "title": ["Python Developer"],
            "company": ["Tech Corp"],
            "site": ["linkedin"],
            "score": [85],
            "clasificacion": ["Excelente"],
            "stack_principal": ["Python/Django"],
            "job_url": ["https://example.com/job/1"],
            "location": ["Bogotá"],
            "description": [""],
            "detected_technologies": ["Python"],
            "search_term": ["Python"],
            "salary": [""],
            "date_posted": [""],
            "full_description": ["Python Django description"],
        })

        result = export_to_csv(df, filename="test_custom.csv")

        assert "test_custom.csv" in result
        assert os.path.exists(result)

        # Cleanup
        os.remove(result)
