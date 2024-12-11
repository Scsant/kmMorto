from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
import csv
import os


# Classe da Interface Gráfica
class RegistroKMApp(App):
    def build(self):
        # Layout principal
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Campos do formulário
        self.label_data = Label(text="Data:")
        self.input_data = TextInput(hint_text="DD/MM/AAAA")

        self.label_btf = Label(text="BTF:")
        self.input_btf = TextInput(hint_text="Ex: 1", input_filter="int")

        self.label_frota = Label(text="Frota:")
        self.input_frota = TextInput(hint_text="Ex: 44045", input_filter="int")

        self.label_distancia = Label(text="Distância (KM):")
        self.input_distancia = TextInput(hint_text="Ex: 16.3", input_filter="float")

        self.label_motivo = Label(text="Motivo:")
        self.input_motivo = TextInput(hint_text="Motivo do deslocamento")

        # Botão para salvar
        self.botao_salvar = Button(text="Salvar", on_press=self.salvar_dados)

        # Mensagem de status
        self.label_status = Label(text="")

        # Adicionar os widgets ao layout
        self.layout.add_widget(self.label_data)
        self.layout.add_widget(self.input_data)

        self.layout.add_widget(self.label_btf)
        self.layout.add_widget(self.input_btf)

        self.layout.add_widget(self.label_frota)
        self.layout.add_widget(self.input_frota)

        self.layout.add_widget(self.label_distancia)
        self.layout.add_widget(self.input_distancia)

        self.layout.add_widget(self.label_motivo)
        self.layout.add_widget(self.input_motivo)

        self.layout.add_widget(self.botao_salvar)
        self.layout.add_widget(self.label_status)

        return self.layout

    def salvar_dados(self, instance):
        # Capturar os dados do formulário
        data = self.input_data.text
        btf = self.input_btf.text
        frota = self.input_frota.text
        distancia = self.input_distancia.text
        motivo = self.input_motivo.text

        # Validação básica
        if not (data and btf and frota and distancia and motivo):
            self.label_status.text = "[ERRO] Preencha todos os campos!"
            return

        # Salvar os dados no arquivo CSV
        arquivo_csv = "dados_km_morto.csv"
        existe = os.path.exists(arquivo_csv)

        with open(arquivo_csv, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if not existe:  # Criar cabeçalho se o arquivo não existir
                writer.writerow(["Data", "BTF", "Frota", "Distância (KM)", "Motivo"])
            writer.writerow([data, btf, frota, distancia, motivo])

        # Atualizar a mensagem de status
        self.label_status.text = "[SUCESSO] Registro salvo com sucesso!"

        # Limpar os campos do formulário
        self.input_data.text = ""
        self.input_btf.text = ""
        self.input_frota.text = ""
        self.input_distancia.text = ""
        self.input_motivo.text = ""


# Rodar o aplicativo
if __name__ == "__main__":
    RegistroKMApp().run()
