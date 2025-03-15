document.addEventListener("DOMContentLoaded", function () {
    const salaSelect = document.getElementById("sala");
    const irParaDiasButton = document.getElementById("irParaDias");

    // Carregar salas
    async function carregarSalas() {
        try {
            const response = await fetch("https://esportes-x2p0.onrender.com/api/salas");
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
        irParaDiasButton.disabled = !this.value;
    });

    // Redirecionar para a página de dias
    irParaDiasButton.addEventListener("click", function () {
        const salaId = salaSelect.value;
        if (salaId) {
            window.location.href = `sala.html?sala=${salaId}`;
        }
    });

    // Carregar salas ao iniciar a página
    carregarSalas();
});

document.addEventListener("DOMContentLoaded", function () {
    const urlParams = new URLSearchParams(window.location.search);
    const salaId = urlParams.get("sala");
    const diasContainer = document.getElementById("diasContainer");

    // Carregar dias
    async function carregarDias() {
        try {
            const response = await fetch(`https://esportes-x2p0.onrender.com/api/dias/${salaId}`);
            const dias = await response.json();

            dias.forEach(dia => {
                const diaButton = document.createElement("button");
                diaButton.textContent = dia;
                diaButton.classList.add("dia-button");
                diaButton.addEventListener("click", function () {
                    window.location.href = `horarios.html?sala=${salaId}&dia=${dia}`;
                });
                diasContainer.appendChild(diaButton);
            });
        } catch (error) {
            console.error("Erro ao carregar dias:", error);
        }
    }

    carregarDias();
});

document.addEventListener("DOMContentLoaded", function () {
    const urlParams = new URLSearchParams(window.location.search);
    const salaId = urlParams.get("sala");
    const dia = urlParams.get("dia");
    const horariosContainer = document.getElementById("horariosContainer");

    // Carregar horários
    async function carregarHorarios() {
        try {
            const response = await fetch(`https://esportes-x2p0.onrender.com/api/horarios/${salaId}/${dia}`);
            const horarios = await response.json();

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

    carregarHorarios();
});
