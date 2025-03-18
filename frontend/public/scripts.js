document.addEventListener("DOMContentLoaded", function () {
    // Configurar o Amplify
    fetch('https://main.d1636gox262hyh.amplifyapp.com/aws-exports.js')
        .then(response => response.text())
        .then(data => {
            const awsconfig = eval(data); // Evite usar eval se possível, para segurança.
            Amplify.configure(awsconfig);
        })
        .catch(error => {
            console.error("Erro ao carregar aws-exports.js:", error);
        });

    // Função para carregar as salas
    const salaSelect = document.getElementById("sala");
    const irParaSelecaoButton = document.getElementById("irParaSelecao");

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
