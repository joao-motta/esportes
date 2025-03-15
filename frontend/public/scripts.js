document.addEventListener("DOMContentLoaded", function () {
    const salaSelect = document.getElementById("sala");
    const diaSelect = document.getElementById("dia");
    const horarioSelect = document.getElementById("horario");
    const videosContainer = document.getElementById("videos");

    // Função para carregar as salas
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

    // Carregar dias ao selecionar uma sala
    salaSelect.addEventListener("change", async function () {
        diaSelect.innerHTML = '<option value="">Selecione um dia</option>';
        horarioSelect.innerHTML = '<option value="">Selecione um horário</option>';
        diaSelect.disabled = true;
        horarioSelect.disabled = true;

        if (!this.value) return;

        try {
            const response = await fetch(`https://esportes-x2p0.onrender.com/api/dias/${this.value}`);
            const dias = await response.json();

            if (dias.length > 0) {
                diaSelect.disabled = false;
                dias.forEach(dia => {
                    const option = document.createElement("option");
                    option.value = dia;
                    option.textContent = dia;
                    diaSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error("Erro ao carregar dias:", error);
        }
    });

    // Carregar horários ao selecionar um dia
    diaSelect.addEventListener("change", async function () {
        horarioSelect.innerHTML = '<option value="">Selecione um horário</option>';
        horarioSelect.disabled = true;

        if (!this.value) return;

        try {
            const response = await fetch(`https://esportes-x2p0.onrender.com/api/horarios/${salaSelect.value}/${this.value}`);
            const horarios = await response.json();

            if (horarios.length > 0) {
                horarioSelect.disabled = false;
                horarios.forEach(horario => {
                    const option = document.createElement("option");
                    option.value = horario;
                    option.textContent = horario;
                    horarioSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error("Erro ao carregar horários:", error);
        }
    });

    // Carregar vídeos ao selecionar um horário
    horarioSelect.addEventListener("change", async function () {
        videosContainer.innerHTML = "";

        if (!this.value) return;

        try {
            const response = await fetch(`https://esportes-x2p0.onrender.com/api/videos/${salaSelect.value}/${diaSelect.value}/${this.value}`);
            const videos = await response.json();

            if (videos.length > 0) {
                videos.forEach(video => {
                    const videoElement = document.createElement("div");
                    videoElement.classList.add("video-item");
                    videoElement.innerHTML = `
                        <img src="${video.thumbnail}" alt="${video.nome}">
                        <p>${video.nome}</p>
                        <a href="${video.url}" download>Baixar</a>
                    `;
                    videosContainer.appendChild(videoElement);
                });
            } else {
                videosContainer.innerHTML = "<p>Nenhum vídeo disponível.</p>";
            }
        } catch (error) {
            console.error("Erro ao carregar vídeos:", error);
        }
    });

    // Carregar as salas ao iniciar a página
    carregarSalas();
});
