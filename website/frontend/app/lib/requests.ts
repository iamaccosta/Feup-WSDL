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

export async function getBusStops(city: string) {
    try {
        const response = await fetch(`http://localhost:5000/${city}/BusStop`, {
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

export async function getDiaryReport(city: string) {
    try {
        const response = await fetch(`http://localhost:5000/${city}/forecast`, {
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

export async function getBusInfo(city: string, busStopId: string) {
    try {
        const response = await fetch(`http://localhost:5000/${city}/BusStop/stop_${busStopId}`, {
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