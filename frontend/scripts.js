/*
  --------------------------------------------------------------------------------------
  Função para obter a lista existente do servidor via requisição GET
  --------------------------------------------------------------------------------------
*/
const getList = async () => {
  let url = 'http://127.0.0.1:5000/documentos';
  fetch(url, {
    method: 'get',
  })
    .then((response) => response.json())
    .then((data) => {
      data.documentos.forEach(item => insertList(item.tipo_documento, item.nr_documento, item.razao_social, item.valor, item.data_vencimento, item.status));
    })
    .catch((error) => {
      console.error('Error:', error);
    });
}

/*
  --------------------------------------------------------------------------------------
  Chamada da função para carregamento inicial dos dados
  --------------------------------------------------------------------------------------
*/
getList()


/*
  --------------------------------------------------------------------------------------
  Função para colocar um item na lista do servidor via requisição POST
  --------------------------------------------------------------------------------------
*/
const postItem = async (inputDocumentType, inputDocumentNumber, inputCompanyName, inputPrice, inputDueDate, inputStatus) => {
  const formData = new FormData();
  formData.append('tipo_documento', inputDocumentType);
  formData.append('nr_documento', inputDocumentNumber);
  formData.append('razao_social', inputCompanyName);
  formData.append('valor', inputPrice);
  formData.append('data_vencimento', inputDueDate);
  formData.append('status', inputStatus);
  

  let url = 'http://127.0.0.1:5000/documento';
  fetch(url, {
    method: 'post',
    body: formData
  })
    .then((response) => response.json())
    .catch((error) => {
      console.error('Error:', error);
    });
}


/*
  --------------------------------------------------------------------------------------
  Função para criar um botão close para cada item da lista
  --------------------------------------------------------------------------------------
*/
const insertButton = (parent) => {
  let span = document.createElement("span");
  let txt = document.createTextNode("\u00D7");
  span.className = "close";
  span.appendChild(txt);
  parent.appendChild(span);
}


/*
  --------------------------------------------------------------------------------------
  Função para remover um item da lista de acordo com o click no botão close
  --------------------------------------------------------------------------------------
*/
const removeElement = () => {
  let close = document.getElementsByClassName("close");
  let i;
  for (i = 0; i < close.length; i++) {
    close[i].onclick = function () {
      let row = this.parentElement.parentElement;
      const nr_documento = row.getElementsByTagName('td')[1].textContent;
      const razao_social = row.getElementsByTagName('td')[2].textContent;
      if (confirm("Você tem certeza?")) {
        row.remove();

        const item = { nr_documento, razao_social };
        deleteItem(item);
        alert("Removido!");
      }
    }
  }
}

/*
  --------------------------------------------------------------------------------------
  Função para deletar um item da lista do servidor via requisição DELETE
  --------------------------------------------------------------------------------------
*/
const deleteItem = (item) => {
  console.log(item)
  let url = `http://127.0.0.1:5000/documento?nr_documento=${item.nr_documento}&razao_social=${item.razao_social}`;
  fetch(url, {
    method: 'delete'
})
    .then((response) => response.json())
    .catch((error) => {
      console.error('Error:', error);
    });
}

/*
  --------------------------------------------------------------------------------------
  Função para adicionar um novo item com nome, quantidade e valor 
  --------------------------------------------------------------------------------------
*/
const newItem = () => {
  let inputDocumentType = document.getElementById("newDocumentType").value;
  let inputDocumentNumber = document.getElementById("newDocumentNumber").value;
  let inputCompanyName = document.getElementById("newCompanyName").value;
  let inputPrice = document.getElementById("newPrice").value;
  let inputDueDate = document.getElementById("newDueDate").value;
  let inputStatus = document.getElementById("newStatus").value;

    insertList(inputDocumentType, inputDocumentNumber, inputCompanyName, inputPrice, inputDueDate, inputStatus)
    postItem(inputDocumentType, inputDocumentNumber, inputCompanyName, inputPrice, inputDueDate, inputStatus)
    alert("Documento adicionado!")
  }

/*
  --------------------------------------------------------------------------------------
  Função para inserir items na lista apresentada
  --------------------------------------------------------------------------------------
*/
const insertList = (documentType, documentNumber, companyName, price, dueDate, status) => {
  var item = [documentType, documentNumber, companyName, price, dueDate, status]
  var table = document.getElementById('myTable');
  var row = table.insertRow();

  for (var i = 0; i < item.length; i++) {
    var cel = row.insertCell(i);
    cel.textContent = item[i];
  }
  insertButton(row.insertCell(-1))
  document.getElementById("newDocumentType").value = "";
  document.getElementById("newDocumentNumber").value = "";
  document.getElementById("newCompanyName").value = "";
  document.getElementById("newPrice").value = "";
  document.getElementById("newDueDate").value = "";
  document.getElementById("newStatus").value = "";

  removeElement()
}
/*
  --------------------------------------------------------------------------------------
  Função para pesquisar um item único
  !! Função descontinuada pois ainda precisa de mais testes e validações, será evoluido na proxima entrega !!
  --------------------------------------------------------------------------------------
*/
/*
const searchItem = (inputDocumentNumber, inputCompanyName) => {
  let url = `http://127.0.0.1:5000/documento?nr_documento=${inputDocumentNumber}&razao_social=${inputCompanyName}`;
  fetch(url, {
    method: 'get'
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.documento) {
        // Item encontrado, faça o que for necessário aqui
        alert("Item encontrado!");
        // Você pode exibir os detalhes do item ou realizar outras ações
        console.log(data.documento);
      } else {
        // Item não encontrado, trate a situação aqui
        alert("Item não encontrado.");
      }
    })
    .catch((error) => {
      console.error('Error:', error);
    });
}
*/