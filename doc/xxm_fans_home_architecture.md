# XXM Fans Home Architecture Diagram

```mermaid
graph TD
    %% Frontend Layer
    subgraph Frontend["Frontend (Vue.js 3 + Element Plus)"]
        subgraph Views["Views"]
            SongListView[SongList.vue]
            TopChartView[TopChart.vue]
            FootprintView[Footprint.vue]
            RecordListView[RecordList.vue]
        end
        
        subgraph Components["Components"]
            SongSearch[SongSearch.vue]
            CollectionGallery[CollectionGallery.vue]
            AdvancedBlindBox[AdvancedBlindBox.vue]
            LuckyWheel[LuckyWheel.vue]
            RandomSongDialog[RandomSongDialog.vue]
        end
        
        subgraph Routing["Routing"]
            VueRouter[Vue Router]
        end
    end

    %% API Layer
    subgraph API["API Layer (Django REST Framework)"]
        subgraph MainAPI["Main App APIs"]
            SongAPI[Song API<br/>/api/songs/]
            SongRecordAPI[Song Record API<br/>/api/songs/{id}/records/]
            StyleAPI[Style API<br/>/api/styles/]
            TagAPI[Tag API<br/>/api/tags/]
            TopSongsAPI[Top Songs API<br/>/api/top_songs/]
            RandomSongAPI[Random Song API<br/>/api/random-song/]
            RecommendationAPI[Recommendation API<br/>/api/recommendation/]
        end
        
        subgraph FansDIYAPI["FansDIY App APIs"]
            CollectionAPI[Collection API<br/>/api/fansDIY/collections/]
            WorkAPI[Work API<br/>/api/fansDIY/works/]
        end
    end

    %% Backend Layer
    subgraph Backend["Backend (Django + Python)"]
        subgraph Django["Django Framework"]
            DjangoCore[Django Core]
            DRF[Django REST Framework]
            Admin[Django Admin]
        end
        
        subgraph Apps["Django Apps"]
            MainApp[Main App]
            FansDIYApp[FansDIY App]
        end
        
        subgraph Models["Data Models"]
            SongsModel[Songs Model]
            SongRecordModel[SongRecord Model]
            StyleModel[Style Model]
            TagModel[Tag Model]
            SongStyleModel[SongStyle Model]
            SongTagModel[SongTag Model]
            CollectionModel[Collection Model]
            WorkModel[Work Model]
            RecommendationModel[Recommendation Model]
        end
    end

    %% Database Layer
    subgraph Database["Database (SQLite)"]
        SQLite[SQLite Database]
        SongsTable[Songs Table]
        SongRecordTable[SongRecord Table]
        StyleTable[Style Table]
        TagTable[Tag Table]
        SongStyleTable[SongStyle Table]
        SongTagTable[SongTag Table]
        CollectionTable[Collection Table]
        WorkTable[Work Table]
        RecommendationTable[Recommendation Table]
    end

    %% External Services
    subgraph External["External Services"]
        Bilibili[Bilibili API<br/>(for BV data)]
        PerformanceTest[Locust<br/>(Performance Testing)]
    end

    %% Connections
    %% Frontend to API
    SongListView --> SongAPI
    SongListView --> StyleAPI
    SongListView --> TagAPI
    SongListView --> RandomSongAPI
    TopChartView --> TopSongsAPI
    RecordListView --> SongRecordAPI
    CollectionGallery --> CollectionAPI
    CollectionGallery --> WorkAPI
    AdvancedBlindBox --> RandomSongAPI
    LuckyWheel --> RandomSongAPI
    RandomSongDialog --> RandomSongAPI
    
    %% API to Backend
    SongAPI --> MainApp
    SongRecordAPI --> MainApp
    StyleAPI --> MainApp
    TagAPI --> MainApp
    TopSongsAPI --> MainApp
    RandomSongAPI --> MainApp
    RecommendationAPI --> MainApp
    CollectionAPI --> FansDIYApp
    WorkAPI --> FansDIYApp
    
    %% Backend to Models
    MainApp --> SongsModel
    MainApp --> SongRecordModel
    MainApp --> StyleModel
    MainApp --> TagModel
    MainApp --> SongStyleModel
    MainApp --> SongTagModel
    MainApp --> RecommendationModel
    FansDIYApp --> CollectionModel
    FansDIYApp --> WorkModel
    
    %% Models to Database
    SongsModel --> SongsTable
    SongRecordModel --> SongRecordTable
    StyleModel --> StyleTable
    TagModel --> TagTable
    SongStyleModel --> SongStyleTable
    SongTagModel --> SongTagTable
    CollectionModel --> CollectionTable
    WorkModel --> WorkTable
    RecommendationModel --> RecommendationTable
    
    %% Database Tables to SQLite
    SongsTable --> SQLite
    SongRecordTable --> SQLite
    StyleTable --> SQLite
    TagTable --> SQLite
    SongStyleTable --> SQLite
    SongTagTable --> SQLite
    CollectionTable --> SQLite
    WorkTable --> SQLite
    RecommendationTable --> SQLite
    
    %% External Services
    Bilibili --> SongRecordModel
    PerformanceTest --> API

    %% Styling
    classDef frontendStyle fill:#64b5f6,stroke:#333,color:#fff;
    classDef apiStyle fill:#81c784,stroke:#333,color:#fff;
    classDef backendStyle fill:#ffb74d,stroke:#333,color:#fff;
    classDef databaseStyle fill:#ba68c8,stroke:#333,color:#fff;
    classDef externalStyle fill:#ff8a65,stroke:#333,color:#fff;
    
    class Frontend,Views,Components,Routing frontendStyle
    class API,MainAPI,FansDIYAPI apiStyle
    class Backend,Django,Apps,Models backendStyle
    class Database,SQLite databaseStyle
    class External,Bilibili,PerformanceTest externalStyle
```

## Architecture Components Overview

### 1. Frontend Layer (Vue.js 3 + Element Plus)
- **Views**: Main pages like SongList, TopChart, Footprint, and RecordList
- **Components**: Reusable UI components like SongSearch, CollectionGallery, AdvancedBlindBox, etc.
- **Routing**: Vue Router for navigation between views

### 2. API Layer (Django REST Framework)
- **Main App APIs**: Endpoints for songs, records, styles, tags, rankings, and recommendations
- **FansDIY App APIs**: Endpoints for collections and works (fan-created content)

### 3. Backend Layer (Django + Python)
- **Django Framework**: Core Django functionality with REST Framework for API creation
- **Apps**: Main app for music management and FansDIY app for fan-created content
- **Models**: Data models representing songs, records, styles, tags, collections, and works

### 4. Database Layer (SQLite)
- **Tables**: Separate tables for each model with proper relationships
- **Relationships**: Foreign keys and many-to-many relationships between tables

### 5. External Services
- **Bilibili API**: For importing BV (Bilibili Video) data
- **Locust**: Performance testing framework

## Key Features Shown in Architecture

1. **Music Management**: Songs, records, styles, and tags with search and filtering capabilities
2. **Fan Content Management**: Collections and works for fan-created content
3. **Ranking System**: Top songs display with different time ranges
4. **Blind Box Feature**: Random song selection with advanced filtering options
5. **Data Visualization**: Charts and statistics display
6. **Performance Testing**: Integration with Locust for load testing