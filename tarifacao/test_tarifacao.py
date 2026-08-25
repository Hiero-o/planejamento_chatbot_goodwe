import json
import tempfile
import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from tarifacao.auth import UserStore
from tarifacao.calculator import PricingCalculator
from tarifacao.models import Establishment
from tarifacao.repository import EstablishmentRepository
from tarifacao.session_repository import SessionRepository
from services.question_processor import _create_random_tariff_session


class PricingTests(unittest.TestCase):
    def test_simulates_peak_session_with_establishment_margin(self):
        result = PricingCalculator().simulate(
            "estabelecimento_01",
            "charger_01",
            datetime(2026, 8, 23, 18, 0),
            40,
            7.2,
        )
        self.assertEqual(result.energia_kwh, Decimal("4.800"))
        self.assertEqual(result.periodo, "ponta")
        self.assertEqual(result.subtotal_energia, Decimal("8.10"))
        self.assertEqual(result.margem_estabelecimento, Decimal("0.81"))
        self.assertEqual(result.custo_total, Decimal("8.91"))

    def test_flag_and_configured_taxes_are_included(self):
        result = PricingCalculator().simulate(
            "estabelecimento_01",
            "charger_01",
            datetime(2026, 8, 23, 10, 0),
            60,
            1,
            "amarela",
        )
        self.assertEqual(result.adicional_bandeira_kwh, Decimal("0.01885"))
        self.assertEqual(result.total_impostos, Decimal("0.00"))

    def test_can_add_establishment_without_changing_calculator(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path("tarifacao/estabelecimentos.json")
            destination = Path(folder) / "estabelecimentos.json"
            destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            repository = EstablishmentRepository(destination)
            repository.add_establishment(Establishment("novo", "Novo local", "SP", Decimal("2")))
            data = json.loads(destination.read_text(encoding="utf-8"))
            self.assertEqual(data["estabelecimentos"][-1]["estabelecimento_id"], "novo")

    def test_password_is_not_stored_in_plain_text(self):
        with tempfile.TemporaryDirectory() as folder:
            store = UserStore(Path(folder) / "usuarios.json")
            store.register("erick", "senha-segura")
            self.assertTrue(store.authenticate("erick", "senha-segura"))
            self.assertFalse(store.authenticate("erick", "senha-errada"))
            self.assertNotIn("senha-segura", Path(folder, "usuarios.json").read_text())

    def test_sessions_are_separated_by_establishment_user_and_vehicle(self):
        with tempfile.TemporaryDirectory() as folder:
            session_path = Path(folder) / "sessoes.json"
            repository = SessionRepository(session_path)
            calculator = PricingCalculator()
            result = calculator.simulate(
                "estabelecimento_01", "charger_01", datetime(2026, 8, 23, 9), 30, 7.2,
                usuario_id="usuario_01", veiculo_id="carro_01", session_id="sessao_01",
            )
            repository.save(result)
            self.assertEqual(len(repository.find("estabelecimento_01", "usuario_01", "carro_01")), 1)
            self.assertEqual(repository.find("outro_estabelecimento"), [])
            summary = repository.summary_for_gurai("estabelecimento_01", "usuario_01", "carro_01")
            self.assertIn("sessao_01", summary)
            self.assertIn("Energia total: 3.600 kWh", summary)
            self.assertIn("Custo total registrado:", summary)

    def test_clear_removes_persisted_sessions(self):
        with tempfile.TemporaryDirectory() as folder:
            session_path = Path(folder) / "sessoes.json"
            repository = SessionRepository(session_path)
            result = PricingCalculator().simulate(
                "estabelecimento_01", "charger_01", datetime(2026, 8, 23, 9), 30, 7.2,
            )
            repository.save(result)

            repository.clear()

            reloaded_repository = SessionRepository(session_path)
            self.assertEqual(reloaded_repository.find("estabelecimento_01"), [])

    def test_demo_generation_is_reproducible_in_shape(self):
        with tempfile.TemporaryDirectory() as folder:
            repository = SessionRepository(Path(folder) / "sessoes.json")
            generated = repository.generate_demo_sessions(
                PricingCalculator(), "estabelecimento_01", [("usuario_01", "carro_01")], count=3, seed=7,
            )
            self.assertEqual(len(generated), 3)
            self.assertEqual(len(repository.find("estabelecimento_01", "usuario_01", "carro_01")), 3)

    def test_chat_command_creates_and_persists_named_user_and_vehicle(self):
        with tempfile.TemporaryDirectory() as folder:
            repository = SessionRepository(Path(folder) / "sessoes.json")
            response = _create_random_tariff_session(
                "Crie um usuário com o nome Erick, com o carro Lexus, e coloque informações aleatórias para o carregamento e me traga o resultado da tarifação.",
                PricingCalculator(),
                repository,
            )
            sessions = repository.find("estabelecimento_01", "Erick", "Lexus")
            self.assertIsNotNone(response)
            self.assertEqual(len(sessions), 1)
            self.assertIn("Custo total", response)

    def test_chat_command_accepts_called_format_with_quotes(self):
        with tempfile.TemporaryDirectory() as folder:
            repository = SessionRepository(Path(folder) / "sessoes.json")
            response = _create_random_tariff_session(
                'Crie um usuário chamado "Pedro" e que tenha o carro "Lexus", então, utilize dados aleatórios para o carregamento. Quero que você me traga as informações sobre a tarifação desse carregamento.',
                PricingCalculator(),
                repository,
            )
            sessions = repository.find("estabelecimento_01", "Pedro", "Lexus")
            self.assertIsNotNone(response)
            self.assertEqual(len(sessions), 1)
            self.assertIn("Pedro", response)
            self.assertIn("Lexus", response)

    def test_chat_command_accepts_vehicle_wording(self):
        with tempfile.TemporaryDirectory() as folder:
            repository = SessionRepository(Path(folder) / "sessoes.json")
            response = _create_random_tariff_session(
                'Crie um usuário chamado "Erick" que use o veículo "Lexus". As demais informações sobre o carregamento podem ser aleatórias. Retorne para mim os dados da tarifação.',
                PricingCalculator(),
                repository,
            )
            sessions = repository.find("estabelecimento_01", "Erick", "Lexus")
            self.assertIsNotNone(response)
            self.assertEqual(len(sessions), 1)
            self.assertIn("Custo total", response)


if __name__ == "__main__":
    unittest.main()
