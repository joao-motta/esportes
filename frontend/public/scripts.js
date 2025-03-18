const Amplify = window.aws_amplify;
import awsconfig from './src/aws-exports';  // Arquivo gerado pelo Amplify CLI
Amplify.configure(awsconfig);

document.addEventListener("DOMContentLoaded", function () {
    const salaSelect = document.getElementById("sala");
    const irParaSelecaoButton = document.getElementById("irParaSelecao");

    // Carregar salas
    async function carregarSalas() {
        try {
            const response = await fetch("http://18.219.146.25:5000/api/salas");
            const salas = await response.json();

            salas.forEach(sala => {
                const option = document.createElement("option");
                option.value = sala.id;
                option.textContent = sala.nome;
                salaSelect.appendChild(option);
            });
        } catch (error) {
            console.error("Erro ao carregar salas:", error);
        }
    }

    // Ativar botão após selecionar a sala
    salaSelect.addEventListener("change", function () {
        irParaSelecaoButton.disabled = !this.value;
    });

    // Redirecionar para a seleção de dia e horário
    irParaSelecaoButton.addEventListener("click", function () {
        const salaId = salaSelect.value;
        if (salaId) {
            window.location.href = `selecionar.html?sala=${salaId}`;
        }
    });

    // Carregar salas ao iniciar a página
    carregarSalas();
});

document.addEventListener("DOMContentLoaded", function () {
    const urlParams = new URLSearchParams(window.location.search);
    const salaId = urlParams.get("sala");
    const diasContainer = document.getElementById("diasContainer");
    const horariosContainer = document.getElementById("horariosContainer");

    // Exibir o nome da sala na página
    const salaNome = document.getElementById("salaNome");
    if (salaId && salaNome) {
        // Buscar nome da sala através do ID
        fetch("http://18.219.146.25:5000/api/salas")
            .then(response => response.json())
            .then(salas => {
                const sala = salas.find(s => s.id == salaId);
                if (sala) {
                    salaNome.textContent = `Sala: ${sala.nome}`; // Exibe o nome da sala
                } else {
                    salaNome.textContent = 'Sala não encontrada';
                }
            })
            .catch(error => console.error("Erro ao buscar nome da sala:", error));
    }

    // Carregar dias
    async function carregarDias() {
        try {
            const response = await fetch(`http://18.219.146.25:5000/api/dias/${salaId}`);
            const dias = await response.json();

            dias.forEach(dia => {
                const diaButton = document.createElement("button");
                diaButton.textContent = dia;
                diaButton.classList.add("dia-button");
                diaButton.addEventListener("click", function () {
                    carregarHorarios(dia);
                });
                diasContainer.appendChild(diaButton);
            });
        } catch (error) {
            console.error("Erro ao carregar dias:", error);
        }
    }

    // Carregar horários
    async function carregarHorarios(dia) {
        try {
            const response = await fetch(`http://18.219.146.25:5000/api/horarios/${salaId}/${dia}`);
            const horarios = await response.json();

            horariosContainer.innerHTML = ''; // Limpa os horários anteriores

            horarios.forEach(horario => {
                const horarioButton = document.createElement("button");
                horarioButton.textContent = horario;
                horarioButton.classList.add("horario-button");
                horariosContainer.appendChild(horarioButton);
            });
        } catch (error) {
            console.error("Erro ao carregar horários:", error);
        }
    }

    carregarDias();
});

