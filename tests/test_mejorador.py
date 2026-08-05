import unittest

from mejorador import Mejorador


class TestMejoradorRefactor(unittest.TestCase):
    def test_tiene_metodos_de_decision_por_tipo_de_mejora(self):
        self.assertTrue(hasattr(Mejorador, "_aplicar_mejora_ruido"))
        self.assertTrue(hasattr(Mejorador, "_aplicar_mejora_brillo"))
        self.assertTrue(hasattr(Mejorador, "_aplicar_mejora_contraste"))
        self.assertTrue(hasattr(Mejorador, "_aplicar_mejora_saturacion"))
        self.assertTrue(hasattr(Mejorador, "_aplicar_mejora_nitidez"))


if __name__ == "__main__":
    unittest.main()
