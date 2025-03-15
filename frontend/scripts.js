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

function carregarDias() {
    let salaId = document.getElementById("salas").value;
    if (!salaId) return;

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

            document.getElementById("selecao-dia").classList.remove("hidden");
        });
}

function carregarHorarios() {
    let salaId = document.getElementById("salas").value;
    let dia = document.getElementById("dias").value;
    if (!salaId || !dia) return;

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
    if (!salaId || !dia || !horario) return;

    fetch(`/api/videos/${salaId}/${dia}/${horario}`)
        .then(response => response.json())
        .then(data => {
            let lista = document.getElementById("lista-videos");
            lista.innerHTML = "";
            data.forEach(video => {
                let li = document.createElement("li");
                let link = document.createElement("a");
                link.href = video.url;
                link.textContent = video.nome;
                link.setAttribute("download", video.nome);
                li.appendChild(link);
                lista.appendChild(li);
            });

            document.getElementById("videos").classList.remove("hidden");
        });
}
