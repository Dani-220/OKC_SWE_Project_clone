import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { LeagueMeta, Lineup, LineupQuery } from '../_models/lineup';
import { BaseService } from './base.service';

@Injectable({ providedIn: 'root' })
export class LineupsService extends BaseService {
  constructor(protected override http: HttpClient) {
    super(http);
  }

  private buildQueryParams(queryParams: Record<string, string | number>): HttpParams {
    return Object.entries(queryParams).reduce(
      (params, [key, value]) => params.set(key, String(value)),
      new HttpParams(),
    );
  }

  private buildDisplayedEndpointWithParams(
    endpoint: string,
    queryParams: Record<string, string | number>,
  ): string {
    const queryString = new URLSearchParams(
      Object.entries(queryParams).map(([key, value]) => [key, String(value)]),
    ).toString();
    return queryString ? `${endpoint}?${queryString}` : endpoint;
  }

  getLineupsLeagueSummary(lineupSize: number = 5): Observable<{
    endpoint: string;
    apiResponse: unknown;
  }> {
    const endpoint = `${this.baseUrl}/lineups`;
    const queryParams = { lineup_size: lineupSize };
    const params = this.buildQueryParams(queryParams);
    const displayedEndpointWithParams = this.buildDisplayedEndpointWithParams(endpoint, queryParams);

    return this.get(endpoint, params).pipe(
      map((data) => ({
        endpoint: displayedEndpointWithParams,
        apiResponse: data,
      })),
    );
  }

  getLineups(query: LineupQuery): Observable<Lineup[]> {
    const queryParams: Record<string, string | number> = { lineup_size: query.lineupSize };
    if (query.teamId) queryParams['team_id'] = query.teamId;
    if (query.playerId) queryParams['player_id'] = query.playerId;
    if (query.minPossessions) queryParams['min_possessions'] = query.minPossessions;
    return this.get(`${this.baseUrl}/lineups`, this.buildQueryParams(queryParams)) as Observable<Lineup[]>;
  }

  getLeagueMeta(): Observable<LeagueMeta> {
    return this.get(`${this.baseUrl}/meta`) as Observable<LeagueMeta>;
  }
}
