let page = 1
let loading = false
let done = false

async function loadMore() {
    if (loading || done) return

    loading = true
    document.getElementById("loading").style.display = "block"

    const res = await fetch(`/api/rolls?page=${page}`)
    const data = await res.json()

    if (data.length === 0) {
        done = true
        document.getElementById("loading").innerText = "No more rows"
        return
    }

    const tbody = document.getElementById("rolls-body")

    for (const row of data) {
        const tr = document.createElement("tr")

        tr.innerHTML = `
            <td>${row.roll}</td>
            <td>${row.frequency}</td>
            <td>${row.solutions}</td>
        `

        tbody.appendChild(tr)
    }

    page += 1
    loading = false
    document.getElementById("loading").style.display = "none"
}

window.addEventListener("scroll", () => {
    if (
        window.innerHeight + window.scrollY
        >= document.body.offsetHeight - 300
    ) {
        loadMore()
    }
})

loadMore()
