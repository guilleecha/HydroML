document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('.col-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const colName = this.getAttribute('data-col');
            const formulaArea = document.getElementById('formula_string');
            formulaArea.value += colName;
            formulaArea.focus();
        });
    });
});