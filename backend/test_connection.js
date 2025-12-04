const APIKEY = "t7L2pR9vT5yK1zX0cM4jN8qG3eU6aB9dF0hO2iS6rV";

async function testConnection() {
    const res = await fetch("https://tubaf-api.felix-heisel.de/v1/rooms/", {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "api-key": APIKEY
        }
    });

    const data = await res.text();  // text() statt json(), weil unklar was API zurückgibt
    console.log(data);
}

testConnection();
