from jobscolombia.scoring import (
    BLACKLIST_COMPANIES,
    calcular_score,
    calcular_score_detallado,
    clasificar_score,
    identificar_stack_principal,
)


class TestCalcularScore:
    def test_python_job_returns_positive_score(self):
        result = calcular_score("Desarrollador Python Django", "Remoto")
        assert result > 0

    def test_exclusion_word_returns_zero(self):
        result = calcular_score("Vendedor de Tiempo Completo", "Enfermera")
        assert result == 0

    def test_no_required_word_returns_zero(self):
        result = calcular_score("Chef de Restaurante", "Cocina")
        assert result == 0

    def test_senior_returns_lower_score(self):
        junior = calcular_score("Desarrollador Python Junior", "Remoto")
        senior = calcular_score("Desarrollador Python Senior", "Remoto")
        assert junior > senior

    def test_remote_modality_boosts_score(self):
        presencial = calcular_score("Desarrollador Python", "Presencial")
        remoto = calcular_score("Desarrollador Python", "Remoto")
        assert remoto > presencial

    def test_score_is_capped_at_100(self):
        result = calcular_score(
            "Python Django FastAPI Senior Remote", "Java Spring Microservices AWS Docker"
        )
        assert result <= 100

    def test_empty_description_uses_title_only(self):
        result = calcular_score("Desarrollador Python Django", "", "")
        assert result > 0

    def test_blacklist_company_returns_zero(self):
        """Blacklisted companies should return score 0 regardless of job content."""
        blacklist = BLACKLIST_COMPANIES
        if blacklist:
            company = blacklist[0]
            result = calcular_score(
                "Desarrollador Python Senior",
                "Python Django AWS Docker",
                "Remoto",
                empresa=company,
            )
            assert result == 0, f"Blacklisted company '{company}' should return 0, got {result}"

    def test_blacklist_case_insensitive(self):
        """Blacklist check should be case insensitive."""
        blacklist = BLACKLIST_COMPANIES
        if blacklist:
            company = blacklist[0].upper()
            result = calcular_score(
                "Desarrollador Python Senior",
                "Python Django AWS Docker",
                "Remoto",
                empresa=company,
            )
            assert result == 0, f"Blacklisted company '{company}' (uppercase) should return 0"

    def test_empresa_none_handled_gracefully(self):
        """calcular_score should handle None empresa without crashing."""
        result = calcular_score("Desarrollador Python", "Remoto", "", empresa=None)
        assert isinstance(result, int)
        assert result >= 0

    def test_empty_string_empresa(self):
        """Empty empresa should not affect scoring."""
        result = calcular_score(
            "Desarrollador Python Django",
            "Remoto",
            "Bogota",
            empresa="",
        )
        assert result > 0


class TestClasificarScore:
    def test_excelente_for_high_score(self):
        assert clasificar_score(90) == "Excelente"
        assert clasificar_score(70) == "Excelente"

    def test_buena_for_medium_score(self):
        assert clasificar_score(69) == "Buena"
        assert clasificar_score(45) == "Buena"

    def test_regular_for_low_score(self):
        assert clasificar_score(44) == "Regular"
        assert clasificar_score(20) == "Regular"

    def test_descartada_for_very_low_score(self):
        assert clasificar_score(19) == "Descartada"
        assert clasificar_score(0) == "Descartada"

    def test_boundary_scores(self):
        """Test exact boundary values for classification."""
        # Boundaries: 70 (Excelente), 45 (Buena), 20 (Regular)
        assert clasificar_score(100) == "Excelente"
        assert clasificar_score(70) == "Excelente"
        assert clasificar_score(69) == "Buena"
        assert clasificar_score(45) == "Buena"
        assert clasificar_score(44) == "Regular"
        assert clasificar_score(20) == "Regular"
        assert clasificar_score(19) == "Descartada"


class TestIdentificarStackPrincipal:
    def test_java_spring_detected(self):
        assert identificar_stack_principal("Java Developer Spring Boot") == "Java/Spring"
        assert identificar_stack_principal("Backend con Spring") == "Java/Spring"

    def test_csharp_dotnet_detected(self):
        assert identificar_stack_principal("C# .NET Developer") == "C#/.NET"
        assert identificar_stack_principal("Backend .NET Core") == "C#/.NET"

    def test_python_django_detected(self):
        assert identificar_stack_principal("Python Django Developer") == "Python/Django"
        assert identificar_stack_principal("Backend FastAPI") == "Python/Django"

    def test_otro_mixto_for_unknown(self):
        assert identificar_stack_principal("Desarrollador Backend") == "Otro/Mixto"
        assert identificar_stack_principal("Ruby on Rails") == "Otro/Mixto"

    def test_empty_string_returns_otro_mixto(self):
        assert identificar_stack_principal("") == "Otro/Mixto"


class TestCalcularScoreDetallado:
    def test_returns_dict_with_required_keys(self):
        result = calcular_score_detallado("Python Developer", "Django", "Remote")
        assert isinstance(result, dict)
        assert "total_score" in result
        assert "clasificacion" in result
        assert "stack" in result
        assert "tech_matches" in result
        assert "seniority_match" in result
        assert "modality_match" in result
        assert "excluded" in result

    def test_with_empresa_blacklisted(self):
        """Empresa in blacklist should mark as excluded."""
        result = calcular_score_detallado(
            "Python Developer",
            "Django AWS",
            "Remote",
            empresa="bairesdev",
        )
        assert result["excluded"] is True

    def test_tech_matches_contains_tuples(self):
        result = calcular_score_detallado(
            "Python Django Developer",
            "Django REST API PostgreSQL",
            "Remote",
        )
        assert isinstance(result["tech_matches"], list)
        for match in result["tech_matches"]:
            assert isinstance(match, tuple)
            assert len(match) == 2

    def test_modality_match_detected(self):
        result = calcular_score_detallado(
            "Python Developer",
            "Django",
            "Remoto",
        )
        assert result["modality_match"] is not None
        assert "remoto" in result["modality_match"][0].lower()

    def test_empty_inputs_returns_zero_score(self):
        """Empty inputs return excluded=False but total_score=0 due to missing required words."""
        result = calcular_score_detallado("", "", "")
        assert result["total_score"] == 0
        assert result["clasificacion"] == "Descartada"
        assert result["excluded"] is False  # excluded only for exclusion_words, not required_words
