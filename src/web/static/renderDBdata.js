function buildTable(data){
    console.log("There are", data.length, "rows of data.");
    var table = document.getElementById('tableData');
    var rows = '';

    for (var i = 0; i < data.length; i++){
        var row = `<tr>
            <td><button class='fav-icon' onclick=changeFav(this)>&#x2661;</button></td>
            <td><a href="${data[i].url}" target="_blank">${data[i].name}</a></td>
            <!--td>${data[i].tel}</td-->
            <td>${data[i].address}</td>
            <!--td>${data[i].city}</td-->
            <!--td>${data[i].state}</td-->
            <!--td>${data[i].zip}</td-->
            <!--td>${data[i].neighborhood}</td-->
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
            if (!dateString) return '';
            const date = new Date(dateString);
            if (isNaN(date)) return '';
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}/${month}/${day}`;
        }
        rows += row;
    }

    table.innerHTML = rows;
    document.getElementById('rowcount').innerHTML = "Total units: " + data.length;
}

function addSortingEventListenerToTable(){
    let table = document.getElementById('table');
    table.querySelectorAll('th button').forEach((th, position) => {
        th.addEventListener('click', evt => sortTable(position+1));
    });
}

function resetOption(col){
    var minRent = Number(document.getElementById('minRent').value);
    var maxRent = Number(document.getElementById('maxRent').value);
    if (col == 'minRent' && minRent > maxRent){
        document.getElementById('maxRent').value = minRent;
    }
    else if (col == 'maxRent' && maxRent < minRent){
        document.getElementById('minRent').value = maxRent;
    }
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
function changeFav(element){
    var fav = element.innerHTML;
    if (fav == '♡'){
        element.innerHTML = '♥';
    }
    else{
        element.innerHTML = '♡';
    }
}   

function sortTable(colnum) {
    var ths = document.querySelectorAll('#table th button');
    ths.forEach(th => {
        console.log(th.innerHTML);
        if (th.innerHTML.includes(' ▼') || th.innerHTML.includes(' ▲')){
            th.innerHTML = th.innerHTML.substring(0, th.innerHTML.length - 1);
        }
    });
    var th = document.querySelector('#table th:nth-child(' + (colnum) + ') button');
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
        text += ' &#9650';
    }else{
        rows = rows.sort((r1, r2) => {
            let t1 = r1.querySelector(qs);
            let t2 = r2.querySelector(qs);
            return compareValues(t2.innerText, t1.innerText, type);
        })
        th.setAttribute('data-order', 'desc');
        text += ' &#9660';
    }

   th.innerHTML = text;
   rows.forEach(row => tbody.appendChild(row));
}

function tableFilterBedBath(){
    bedNum = document.getElementById('bedNum').value;
    bathNum = document.getElementById('bathNum').value;

    var table = document.getElementById('tableData');
    var tr = table.getElementsByTagName('tr');
    var count = 0;
    for (var i = 0; i < tr.length; i++){
        tr[i].style.display = '';
        var tdBed = tr[i].getElementsByTagName('td')[7];
        var tdBath = tr[i].getElementsByTagName('td')[8];
        if (tdBed && bedNum != 'X'){
            if (bedNum.includes('+')){
                bedNum = bedNum.replace('+', '');
                if (parseFloat(tdBed.innerHTML) < bedNum){
                    tr[i].style.display = 'none';
                }
            }
            else{
                if (parseInt(tdBed.innerHTML) != bedNum){
                    tr[i].style.display = 'none';
                }
            }
        }
        if (tdBath && bathNum != 'X'){
            if (bathNum.includes('+')){
                bathNum = bathNum.replace('+', '');
                if (parseFloat(tdBath.innerHTML) < bathNum){
                    tr[i].style.display = 'none';
                }
            }
            else{
                if (parseInt(tdBath.innerHTML) != bathNum){
                    tr[i].style.display = 'none';
                }
            }
        }
        if (tr[i].style.display == ''){
            count += 1;
        }
    }

    document.getElementById('rowcount').innerHTML = "Total units: " + count;
}

function tableFilterRent(){
    tableFilterBedBath();
    var table = document.getElementById('tableData');
    var tr = table.getElementsByTagName('tr');
    var minRent = document.getElementById('minRent').value;
    var maxRent = document.getElementById('maxRent').value;
    var count = 0;
    console.log(minRent, maxRent);
    for (var i = 0; i < tr.length; i++){
        var tdRent = tr[i].getElementsByTagName('td')[9];
        if (tdRent){
            if (minRent != ''){
                if (parseFloat(tdRent.innerHTML.replace(/[^0-9.-]+/g,"")) < parseFloat(minRent)){
                    tr[i].style.display = 'none';
                }
            }
            if (maxRent != ''){
                if (parseFloat(tdRent.innerHTML.replace(/[^0-9.-]+/g,"")) > parseFloat(maxRent)){
                    tr[i].style.display = 'none';
                }
            }
        }
        if (tr[i].style.display == ''){
            count += 1;
        }
    }

    document.getElementById('rowcount').innerHTML = "Total units: " + count;
}

function clearFilterInput() {
    var inputBed = document.getElementById("bedNum");
    var inputBath = document.getElementById("bathNum");
    var inputMin = document.getElementById("minRent"); 
    var inputMax = document.getElementById("maxRent");
    inputBed.value = "X";
    inputBath.value = "X";
    inputMin.value = "";
    inputMax.value = "";
    tableFilterBedBath();
  }

function buildTopManagement(data) {
    let mgmtTable = document.getElementById("topManagementTable");
    let rows = "";
    data.forEach(row => {
        rows += `<tr>
            <td>${row.management}</td>
            <td>${Number(row.avg_rating).toFixed(2)}</td>
            <td>${row.rating_count}</td>
        </tr>`;
    });
    mgmtTable.innerHTML = rows;
}

function buildTopNeighborhood(data) {
    let nbTable = document.getElementById("topNeighborhoodTable");
    let rows = "";
    data.forEach(row => {
        rows += `<tr>
            <td>${row.neighborhood}</td>
            <td>$${Number(row.avg_price_per_sqft).toFixed(2)}</td>
            <td>${row.unit_count}</td>
        </tr>`;
    });
    nbTable.innerHTML = rows;
}
