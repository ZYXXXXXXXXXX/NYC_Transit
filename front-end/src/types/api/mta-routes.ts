// Base route interface that all transportation modes would share
export interface BaseRoute {
    id: string;
    short_name: string;
    long_name: string;
}

// Subway-specific implementation
export interface SubwayRoute extends BaseRoute {
    color: string;
    text_color: string;
}

// TODO: Future bus route implementation might look like:
// export interface BusRoute extends BaseRoute {
//     borough: string;
//     // Other bus-specific properties
// }