from src.scoring import calcular_score, clasificar_score, identificar_stack_principal


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
