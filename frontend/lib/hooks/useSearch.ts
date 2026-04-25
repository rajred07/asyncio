import { useQuery } from '@tanstack/react-query';
import { SearchService, SearchResponse } from '@/lib/api/services/SearchService';

/**
 * useSearch — React Query hook wrapping the /api/search endpoint.
 *
 * - Fires only when query is >= 2 characters (mirrors backend guard)
 * - Caches results for 30 seconds (searches change infrequently)
 */
export function useSearch(
    query: string,
    type: 'all' | 'playlists' | 'users' = 'all',
) {
    return useQuery<SearchResponse>({
        queryKey: ['search', query.trim(), type],
        queryFn: () => SearchService.search(query.trim(), type),
        enabled: query.trim().length >= 2,
        staleTime: 30 * 1000,       // 30s cache
        refetchOnWindowFocus: false,
    });
}
