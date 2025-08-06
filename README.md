# Calendar Service

Um serviço de calendário moderno e eficiente para gerenciamento de eventos e agendamentos.

## 📋 Sobre o Projeto

O Calendar Service é uma solução robusta desenvolvida em FastAPI para sincronização de jogos do IFSports com o Google Calendar.

## ✨ Funcionalidades

- 🎯 Cadastrar eventos de partidas
- 📱 API RESTful para integração

## 🚀 Tecnologias Utilizadas

- **Python** - Linguagem principal
- **FastAPI** - Framework web
- **SQLAlchemy** - ORM para banco de dados
- **PostgreSQL** - Banco de dados
- **Docker** - Containerização

## 📦 Instalação

### Pré-requisitos

- Python 3.8+
- Docker
- Banco de dados (PostgreSQL)

### Instalação Local

1. Clone o repositório:
```bash
git clone https://github.com/ifsports/calendar-service.git
cd calendar-service
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
# Edite o arquivo .env com suas configurações
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=

SQLALCHEMY_DATABASE_URL=
```

5. Execute as migrações:
```bash
python manage.py migrate
```

6. Inicie o servidor:
```bash
python main.py
```

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 👨‍💻 Autor

**IFSports Team**

- GitHub: [@ifsports](https://github.com/ifsports)

---

⭐ Se este projeto foi útil para você, considere dar uma estrela no repositório!
