async function getMedicine() {
    const name = document.querySelector("input[name='medicine-name']").value;
    const quantity = document.querySelector("input[name='medicine-quantity']").value;
    const dosage = document.querySelector("input[name='medicine-dosage']").value;
    console.log(name)
    console.log(quantity)
    console.log(dosage)
    try {
        const res = await fetch(`/api/medicines`, {
            method: "POST",
            body: JSON.stringify({
                name,
                quantity,
                dosage
            }),
            headers: {
      "Content-Type": "application/json",
    },
        })
        const data = await res.json()
        return data
    } catch(e) {
        console.log(e)
    }
}

window.onload = function() {
    const element = document.querySelector('#medicine-form');
    element.addEventListener('submit', event => {
      event.preventDefault();
      const medicine = getMedicine()
      // Hien thi thong tin thuoc len phieu kham
    });
}
