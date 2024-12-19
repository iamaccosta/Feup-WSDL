export async function getStaticInfo(city: string) {
    try {
        const response = await fetch(`http://localhost:5000/${city}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
            },
        })
        
        if (!response.ok) {
            return null;
        }

        const result = await response.json()
        return result
    } catch (e) {
        return null;
    }
}
