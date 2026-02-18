import axios from 'axios';
import { locationAPI, propertyAPI } from '../api';

jest.mock('axios');

describe('API Service Layer', () => {
    const mockAxios = axios.create();

    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('locationAPI.search calls correct endpoint', async () => {
        const mockResponse = { data: { found: true, municipality: { id: 1, name: 'Milano' } } };
        mockAxios.post.mockResolvedValue(mockResponse);

        const result = await locationAPI.search('Milano');

        expect(mockAxios.post).toHaveBeenCalledWith('/locations/search', { query: 'Milano' });
        expect(result).toEqual(mockResponse.data);
    });

    test('propertyAPI.getMunicipalityPrices calls correct endpoint', async () => {
        const mockResponse = { data: [{ year: 2023, avg_price: 5000 }] };
        mockAxios.get.mockResolvedValue(mockResponse);

        const result = await propertyAPI.getMunicipalityPrices(1);

        expect(mockAxios.get).toHaveBeenCalledWith(expect.stringContaining('/prices/municipality/1'));
        expect(result).toEqual(mockResponse.data);
    });
});
