function buildTable(data){
    console.log(data.length);
    var table = document.getElementById('tableData');
    var rows = '';

    for (var i = 0; i < data.length; i++){
        var row = `<tr>
            <td><a href="${data[i].url}" target="_blank">${data[i].name}</a></td>
            <!-- <td>${data[i].tel}</td> -->
            <td>${data[i].address}</td>
            <td>${data[i].city}</td>
            <td>${data[i].state}</td>
            <td>${data[i].zip}</td>
            <td>${data[i].neighborhood}</td>
            <td>${data[i].built}</td>
            <td>${data[i].units}</td>
            <td>${data[i].stories}</td>
            <!-- <td>${data[i].management}</td> -->
            <td>${data[i].unit_no}</td>
            <td>${data[i].unit_beds}</td>
            <td>${data[i].unit_baths}</td>
            <td>${data[i].unit_price}</td>
            <td>${data[i].unit_sqft}</td>
            <td>${formatDate(data[i].unit_avail)}</td>
        </tr>`;

        function formatDate(dateString) {
            const date = new Date(dateString);
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}/${month}/${day}`;
        }
        rows += row;
    }

    table.innerHTML = rows;
}

function addSortingEventListenerToTable(){
    let table = document.getElementById('table');
    table.querySelectorAll('th').forEach((th, position) => {
        th.addEventListener('click', evt => sortTable(position+1));
    });
}

function compareValues(a, b, type) {
    if (type === 'string') {
        return a.localeCompare(b);
    } else if (type === 'numeric') {
        return Number(a) - Number(b);
    } else if (type === 'date') {
        return new Date(a) - new Date(b);
    }
    else {
        throw new Error('Invalid comparison');
    }
}

function sortTable(colnum) {
    var ths = document.querySelectorAll('#table th');
    ths.forEach(th => {
        console.log(th.innerHTML);
        if (th.innerHTML.includes('▼') || th.innerHTML.includes('▲')){
            th.innerHTML = th.innerHTML.substring(0, th.innerHTML.length - 1);
        }
    });
    
    var th = document.querySelector('#table th:nth-child(' + (colnum) + ')');
    var type = th.getAttribute('data-type');
    var order = th.getAttribute('data-order');
    var text = th.innerHTML;
    
    var tbody = document.getElementById('tableData');
    var rows = Array.from(tbody.querySelectorAll(`tr`));
    let qs = `td:nth-child(${colnum})`;

    if (order == 'desc'){
        rows = rows.sort((r1, r2) => {
            let t1 = r1.querySelector(qs);
            let t2 = r2.querySelector(qs);
            return compareValues(t1.innerText, t2.innerText, type);
        })
        th.setAttribute('data-order', 'asc');
        text += '&#9650'
    }else{
        rows = rows.sort((r1, r2) => {
            let t1 = r1.querySelector(qs);
            let t2 = r2.querySelector(qs);
            return compareValues(t2.innerText, t1.innerText, type);
        })
        th.setAttribute('data-order', 'desc');
        text += '&#9660'
    }

   th.innerHTML = text;
   rows.forEach(row => tbody.appendChild(row));
}
