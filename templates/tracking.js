function addField(n)
{
    var tr = n.parentNode.parentNode.cloneNode(true);
    document.getElementById('tbl').appendChild(tr);
}