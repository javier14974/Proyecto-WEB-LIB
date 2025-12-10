import random
from locust import HttpUser, task, between

class UsuarioSimulado(HttpUser):
    wait_time = between(1, 3)  # tiempo entre requests para simular uso real

    @task(3)
    def cargar_home(self):
        self.client.get("/")

    @task(2)
    def cargar_login(self):
        self.client.get("/login/")

    @task(1)
    def cargar_nosotros(self):
        self.client.get("/nosotros/")

    @task(2)
    def ver_apunte(self):
        # IDs aleatorios simulando apuntes existentes
        apunte_id = random.randint(1, 10)
        self.client.get(f"/apunte/{apunte_id}/")

    @task(1)
    def ver_perfil(self):
        # IDs aleatorios simulando usuarios existentes
        usuario_id = random.randint(1, 10)
        self.client.get(f"/perfil/{usuario_id}/")
