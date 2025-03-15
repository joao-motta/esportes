document.addEventListener("DOMContentLoaded", function () {
    carregarSalas();
});

function carregarSalas() {
    fetch("/api/salas")
        .then(response => response.json())
        .then(data => {
            let select = document.getElementById("salas");
            data.forEach(sala => {
                let option = document.createElement("option");
                option.value = sala.id;
                option.textContent = sala.nome;
                select.appendChild(option);
            });
        });
}

function selecionarSala(salaId) {
    document.getElementById("selecao-dia").classList.remove("hidden");
    carregarDias(salaId);
}

function carregarDias(salaId) {
    fetch(`/api/dias/${salaId}`)
        .then(response => response.json())
        .then(data => {
            let select = document.getElementById("dias");
            select.innerHTML = '<option value="">Selecione um dia</option>';
            data.forEach(dia => {
                let option = document.createElement("option");
                option.value = dia;
                option.textContent = dia;
                select.appendChild(option);
            });
        });
}

function carregarHorarios() {
    let salaId = document.getElementById("salas").value;
    let dia = document.getElementById("dias").value;

    fetch(`/api/horarios/${salaId}/${dia}`)
        .then(response => response.json())
        .then(data => {
            let select = document.getElementById("horarios");
            select.innerHTML = '<option value="">Selecione um horário</option>';
            data.forEach(horario => {
                let option = document.createElement("option");
                option.value = horario;
                option.textContent = horario;
                select.appendChild(option);
            });

            document.getElementById("selecao-horario").classList.remove("hidden");
        });
}

function carregarVideos() {
    let salaId = document.getElementById("salas").value;
    let dia = document.getElementById("dias").value;
    let horario = document.getElementById("horarios").value;

    fetch(`/api/videos/${salaId}/${dia}/${horario}`)
        .then(response => response.json())
        .then(data => {
            let lista = document.getElementById("lista-videos");
            lista.innerHTML = "";
            
            data.forEach(video => {
                let div = document.createElement("div");
                div.classList.add("video-item");
                div.innerHTML = `
                    <img src="${video.thumbnail}" alt="Thumb do ${video.nome}">
                    <p>${video.nome}</p>
                    <a href="${video.url}" download>📥 Baixar</a>
                `;
                lista.appendChild(div);
            });

            document.getElementById("videos").classList.remove("hidden");
        });
}
