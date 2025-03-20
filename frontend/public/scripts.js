document.addEventListener("DOMContentLoaded", function () {
    const salaSelect = document.getElementById("sala");
    const irParaSelecaoButton = document.getElementById("irParaSelecao");

    async function carregarSalas() {
        try {
            const response = await fetch("http://3.141.32.43:5000/api/salas");
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

    salaSelect.addEventListener("change", function () {
        irParaSelecaoButton.disabled = !this.value;
    });

    irParaSelecaoButton.addEventListener("click", function () {
        const salaId = salaSelect.value;
        if (salaId) {
            window.location.href = `selecionar.html?sala=${salaId}`;
        }
    });

    carregarSalas();
});

// Código para selecionar dia, horário e buscar vídeos

document.addEventListener("DOMContentLoaded", function () {
    const urlParams = new URLSearchParams(window.location.search);
    const salaId = urlParams.get("sala");
    const diasContainer = document.getElementById("diasContainer");
    const horariosContainer = document.getElementById("horariosContainer");
    const videosContainer = document.createElement("div");
    videosContainer.id = "videosContainer";
    document.body.appendChild(videosContainer);

    const salaNome = document.getElementById("salaNome");
    if (salaId && salaNome) {
        fetch("http://3.141.32.43:5000/api/salas")
            .then(response => response.json())
            .then(salas => {
                const sala = salas.find(s => s.id == salaId);
                salaNome.textContent = sala ? `Sala: ${sala.nome}` : 'Sala não encontrada';
            })
            .catch(error => console.error("Erro ao buscar nome da sala:", error));
    }

    async function carregarDias() {
        try {
            const response = await fetch(`http://3.141.32.43:5000/api/dias/${salaId}`);
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

    async function carregarHorarios(dia) {
        try {
            const response = await fetch(`http://3.141.32.43:5000/api/horarios/${salaId}/${dia}`);
            const horarios = await response.json();

            horariosContainer.innerHTML = '';

            horarios.forEach(horario => {
                const horarioButton = document.createElement("button");
                horarioButton.textContent = horario;
                horarioButton.classList.add("horario-button");
                horarioButton.addEventListener("click", function () {
                    buscarVideos(dia, horario);
                });
                horariosContainer.appendChild(horarioButton);
            });
        } catch (error) {
            console.error("Erro ao carregar horários:", error);
        }
    }

    async function buscarVideos(dia, horario) {
        try {
            const response = await fetch(`http://3.141.32.43:5000/listavideos?cameraIP=${salaId}&dia=${dia}&horario=${horario}`);
            const videos = await response.json();

            videosContainer.innerHTML = "";

            if (videos.length === 0) {
                videosContainer.innerHTML = "<p>Nenhum vídeo encontrado.</p>";
                return;
            }

            videos.forEach(video => {
                const videoElement = document.createElement("div");
                videoElement.classList.add("video-item");
                videoElement.innerHTML = `
                    <h3>${video.nome}</h3>
                    <img src="${video.thumbnail}" alt="Thumbnail">
                    <a href="${video.url}" target="_blank">Assistir</a>
                `;
                videosContainer.appendChild(videoElement);
            });
        } catch (error) {
            console.error("Erro ao buscar vídeos:", error);
        }
    }

    carregarDias();
});
