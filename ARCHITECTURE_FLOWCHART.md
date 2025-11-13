# 🏗️ Data Cloud Personalization App - Architecture Flowchart

## Complete System Architecture

```mermaid
flowchart TB
    %% ============================================
    %% ENTERPRISE DATA SOURCES
    %% ============================================
    subgraph Sources["<b><font size='+2'>📊 ENTERPRISE DATA SOURCES</font></b>"]
        direction TB
        CRM["<b>🏢 Salesforce CRM</b><br/>Accounts, Contacts, Leads, Cases"]
        Marketing["<b>📧 Marketing Cloud</b><br/>Email, SMS, Push Campaigns"]
        Website["<b>🌐 Website Analytics</b><br/>Product Views, Cart, Purchases"]
        Mobile["<b>📱 Mobile App</b><br/>Push Notifications, In-App Events"]
        WhatsApp["<b>💬 WhatsApp Business API</b><br/>Message Engagement"]
        IoT["<b>🔌 IoT Hub</b><br/>Smart wearables & devices - Vehicle Telematics, Vitals & Health Parameters"]
        Ecommerce["<b>🛒 E-commerce Platform</b><br/>Purchase History, Preferences"]
        Social["<b>📸 Social Media</b><br/>Engagement, Product Reviews, Pvt Fan page interactions"]
        Service["<b>☎️ Contact Center</b><br/>Product Inquiries, Complaints"]
    end

    %% ============================================
    %% DATA CLOUD - DATA INGESTION & PROCESSING
    %% ============================================
    subgraph DataCloud["<b><font size='+2'>☁️ SALESFORCE DATA 360</font></b>"]
        direction TB
        
        subgraph Ingestion["<b>📥 DATA INGESTION</b>"]
            direction LR
            DataStreams["<b>Data Streams</b><br/>Real-time & Batch"]
            Connectors["<b>Data Connectors</b><br/>API, ETL, Streaming"]
        end
        
        subgraph Processing["<b>🔄 DATA PROCESSING</b>"]
            direction TB
            Harmonization["<b>Data Harmonization</b><br/>Schema Mapping, Normalization"]
            IdentityResolution["<b>Identity Resolution</b><br/>Match & Link Records"]
            UnifiedProfile["<b>Unified Profile Creation</b><br/>Single Source of Truth"]
        end
        
        subgraph Insights["<b>💡 INSIGHTS CREATION</b>"]
            direction TB
            UnstructuredProc["<b>Unstructured Data Processing</b><br/>NLP, OCR, Image Recognition, Computer Vision"]
            StructuredProc["<b>Structured Data Processing</b><br/>Calculated Insights, Predictive AI Models"]
            UnstructuredInsights["<b>Unstructured Insights</b><br/>Sentiment, Lifestyle, Health Profile, Purchase Intent, Churn Risk, Hobby, Affinities, Imminent Event"]
            StructuredInsights["<b>Structured Insights</b><br/>Lifetime Value, Loyalty Tier, Favourite Brand, Preferred Channel, Preferred Send Schedule"]
        end
        
        subgraph Profile360["<b>📊 PROFILE 360 GRAPH</b>"]
            direction TB
            UnifiedProfileData["<b>Unified Profile</b><br/>Demographics, Identity"]
            InsightsTimeSeries["<b>Insights on Time Axis:</b><br/>Temporal Structured & Unstructured Insights<br/>Historical & Real-time"]
            Profile360Graph["<b>Dynamic Profile 360 Graph</b><br/>Unified Profile + Temporal Insights"]
        end
    end

    %% ============================================
    %% HEROKU APP - MCP CONNECTION
    %% ============================================
    subgraph HerokuApp["<b><font size='+2'>🚀 HEROKU APPLICATION</font></b>"]
        direction TB
        
        subgraph MCP["<b>🔌 MCP SERVER CONNECTION</b>"]
            direction TB
            MCPConfig["<b>MCP Configuration</b><br/>salesforce-apis"]
            Credentials["<b>Credentials</b><br/>Username/Password/OAuth"]
            MCPTools["<b>MCP Tools</b><br/>query, describe, create"]
        end
        
        subgraph Segmentation["<b>🎯 SMART AUDIENCE BUILDING</b>"]
            direction TB
            SegmentEngine["<b>Segmentation Engine</b><br/>Dynamic Segment Creation"]
            AIAgent["<b>AI Agent</b><br/>Natural Language Processing"]
            CriteriaBuilder["<b>Criteria Builder</b><br/>Multi-dimensional Filtering"]
        end
        
        subgraph Personalization["<b>🎨 PERSONALIZATION ENGINE</b>"]
            direction TB
            PromptGen["<b>Dynamic Prompt Generator</b><br/>Exercise, Brand, Destination, Lifestyle"]
            Gemini["<b>Google Gemini Nano Banana</b><br/>Gemini 2.5 Flash Image"]
            Replicate["<b>Replicate API</b><br/>SDXL + Face-Swap"]
            ImageGen["<b>Personalized Image Generator</b><br/>Face-Swap + Brand Integration"]
            ContentGen["<b>Content Generator</b><br/>Text, Offers, Links"]
        end
        
        subgraph Messaging["<b>📤 MESSAGING ENGINE</b>"]
            direction TB
            ChannelRouter["<b>Channel Router</b><br/>Preferred Channel Detection"]
            EmailEngine["<b>Email Engine</b><br/>HTML, Personalization"]
            SMSEngine["<b>SMS Engine</b><br/>Short-form Content"]
            WhatsAppEngine["<b>WhatsApp Engine</b><br/>Rich Media"]
            PushEngine["<b>Push Engine</b><br/>Notifications"]
        end
    end

    %% ============================================
    %% DELIVERY CHANNELS
    %% ============================================
    subgraph Channels["<b><font size='+2'>📤 DELIVERY CHANNELS</font></b>"]
        direction LR
        Email["<b>📧 Email</b><br/>Marketing Cloud"]
        SMS["<b>💬 SMS</b><br/>Mobile Studio"]
        WhatsAppDel["<b>💬 WhatsApp</b><br/>Business API"]
        Push["<b>🔔 Push Notification</b><br/>Mobile App"]
        WebsiteDel["<b>🌐 Website</b><br/>Personalized Banners"]
    end

    %% ============================================
    %% FLOW CONNECTIONS
    %% ============================================
    
    %% Enterprise Sources to Data Cloud
    CRM --> DataStreams
    Marketing --> DataStreams
    Website --> DataStreams
    Mobile --> DataStreams
    WhatsApp --> DataStreams
    IoT --> DataStreams
    Ecommerce --> DataStreams
    Social --> DataStreams
    Service --> DataStreams
    
    DataStreams --> Connectors
    Connectors --> Harmonization
    
    %% Data Cloud Internal Processing
    Harmonization --> IdentityResolution
    IdentityResolution --> UnifiedProfile
    UnifiedProfile --> UnifiedProfileData
    
    %% Insights Creation
    Harmonization --> UnstructuredProc
    Harmonization --> StructuredProc
    UnstructuredProc --> UnstructuredInsights
    StructuredProc --> StructuredInsights
    
    %% Profile 360 Graph Creation - Both insights are temporal and marry with unified profile
    UnifiedProfileData --> InsightsTimeSeries
    UnstructuredInsights --> InsightsTimeSeries
    StructuredInsights --> InsightsTimeSeries
    InsightsTimeSeries --> Profile360Graph
    UnifiedProfileData --> Profile360Graph
    
    %% Heroku App Connection via MCP
    Profile360Graph --> MCPConfig
    MCPConfig --> Credentials
    Credentials --> MCPTools
    
    %% Segmentation
    MCPTools --> SegmentEngine
    Profile360Graph --> AIAgent
    AIAgent --> SegmentEngine
    SegmentEngine --> CriteriaBuilder
    
    %% Personalization
    Profile360Graph --> PromptGen
    CriteriaBuilder --> PromptGen
    PromptGen --> Gemini
    PromptGen --> Replicate
    Gemini --> ImageGen
    Replicate --> ImageGen
    Profile360Graph --> ContentGen
    ImageGen --> ContentGen
    
    %% Messaging & Routing
    ContentGen --> ChannelRouter
    Profile360Graph --> ChannelRouter
    ChannelRouter --> EmailEngine
    ChannelRouter --> SMSEngine
    ChannelRouter --> WhatsAppEngine
    ChannelRouter --> PushEngine
    
    %% Delivery
    EmailEngine --> Email
    SMSEngine --> SMS
    WhatsAppEngine --> WhatsAppDel
    PushEngine --> Push
    ChannelRouter --> WebsiteDel
    
    %% Feedback Loop
    Email -.->|"Feedback"| DataStreams
    SMS -.->|"Feedback"| DataStreams
    WhatsAppDel -.->|"Feedback"| DataStreams
    Push -.->|"Feedback"| DataStreams
    WebsiteDel -.->|"Feedback"| DataStreams
    
    %% ============================================
    %% ENHANCED STYLING WITH SOFT COLORS
    %% ============================================
    classDef sourceStyle fill:#90caf9,stroke:#1976d2,stroke-width:2px,color:#000000,font-weight:bold
    classDef datacloudStyle fill:#e1bee7,stroke:#ba68c8,stroke-width:2px,color:#000000,font-weight:bold
    classDef ingestionStyle fill:#9fa8da,stroke:#5c6bc0,stroke-width:2px,color:#000000,font-weight:bold
    classDef processingStyle fill:#4db6ac,stroke:#00897b,stroke-width:2px,color:#000000,font-weight:bold
    classDef insightsStyle fill:#ffb74d,stroke:#f57c00,stroke-width:2px,color:#000000,font-weight:bold
    classDef profile360Style fill:#81c784,stroke:#388e3c,stroke-width:3px,color:#000000,font-weight:bold
    classDef herokuStyle fill:#fce4ec,stroke:#f06292,stroke-width:2px,color:#000000,font-weight:bold
    classDef mcpStyle fill:#fff176,stroke:#fbc02d,stroke-width:2px,color:#000000,font-weight:bold
    classDef segmentationStyle fill:#ce93d8,stroke:#8e24aa,stroke-width:2px,color:#000000,font-weight:bold
    classDef personalizationStyle fill:#4dd0e1,stroke:#0097a7,stroke-width:2px,color:#000000,font-weight:bold
    classDef messagingStyle fill:#a5d6a7,stroke:#43a047,stroke-width:2px,color:#000000,font-weight:bold
    classDef channelStyle fill:#64b5f6,stroke:#1976d2,stroke-width:2px,color:#000000,font-weight:bold
    
    class CRM,Marketing,Website,Mobile,WhatsApp,IoT,Ecommerce,Social,Service sourceStyle
    class DataCloud,Ingestion,Processing,Insights,Profile360 datacloudStyle
    class DataStreams,Connectors ingestionStyle
    class Harmonization,IdentityResolution,UnifiedProfile processingStyle
    class UnstructuredProc,StructuredProc,UnstructuredInsights,StructuredInsights insightsStyle
    class UnifiedProfileData,InsightsTimeSeries,Profile360Graph profile360Style
    class HerokuApp,MCP,Segmentation,Personalization,Messaging herokuStyle
    class MCPConfig,Credentials,MCPTools mcpStyle
    class SegmentEngine,AIAgent,CriteriaBuilder segmentationStyle
    class PromptGen,Gemini,Replicate,ImageGen,ContentGen personalizationStyle
    class ChannelRouter,EmailEngine,SMSEngine,WhatsAppEngine,PushEngine messagingStyle
    class Email,SMS,WhatsAppDel,Push,WebsiteDel channelStyle
```

## 📊 Profile 360 Graph - Detailed Architecture

```mermaid
flowchart TB
    %% ============================================
    %% PROFILE 360 GRAPH COMPONENTS
    %% ============================================
    subgraph Profile360["<b><font size='+2'>📊 PROFILE 360 GRAPH ARCHITECTURE</font></b>"]
        direction TB
        
        subgraph Unified["<b>👤 UNIFIED PROFILE</b>"]
            direction TB
            Identity["<b>Identity Resolution</b><br/>• Email Match<br/>• Phone Match<br/>• Device ID Match<br/>• Social ID Match"]
            Demographics["<b>Demographics</b><br/>• Name, Age, Location<br/>• Contact Information<br/>• Device Information"]
            UnifiedRecord["<b>Unified Individual Record</b><br/>Single Source of Truth"]
        end
        
        subgraph Insights["<b>💡 INSIGHTS LAYER</b>"]
            direction TB
            
            subgraph Structured["<b>📋 STRUCTURED INSIGHTS</b>"]
                direction TB
                StructuredProc["<b>Structured Data Processing</b><br/>• Calculated Insights<br/>• Predictive AI Models"]
                StructuredInsights["<b>Structured Insights</b><br/>• Lifetime Value<br/>• Loyalty Tier<br/>• Favourite Brand<br/>• Preferred Channel<br/>• Preferred Send Schedule"]
            end
            
            subgraph Unstructured["<b>📝 UNSTRUCTURED INSIGHTS</b>"]
                direction TB
                UnstructuredProc["<b>Unstructured Data Processing</b><br/>• NLP (Natural Language Processing)<br/>• OCR (Optical Character Recognition)<br/>• Image Recognition<br/>• Computer Vision"]
                UnstructuredInsights["<b>Unstructured Insights</b><br/>• Sentiment<br/>• Lifestyle<br/>• Health Profile<br/>• Purchase Intent"]
            end
        end
        
        subgraph TimeAxis["<b>⏱️ TIME AXIS DIMENSION</b>"]
            direction TB
            Historical["<b>Historical Data</b><br/>• Past 30 Days<br/>• Past 90 Days<br/>• Past 1 Year<br/>• Lifetime"]
            RealTime["<b>Real-Time Data</b><br/>• Last Hour<br/>• Last 24 Hours<br/>• Current State"]
            Trends["<b>Trend Analysis</b><br/>• Engagement Trends<br/>• Behavior Changes<br/>• Milestone Progression<br/>• Sentiment Shifts"]
        end
        
        subgraph Graph["<b>🕸️ PROFILE 360 GRAPH</b>"]
            direction TB
            Nodes["<b>Graph Nodes</b><br/>• Individual<br/>• Insights<br/>• Events<br/>• Relationships"]
            Edges["<b>Graph Edges</b><br/>• Temporal Links<br/>• Causal Links<br/>• Correlation Links"]
            GraphStructure["<b>Dynamic Profile 360 Graph Structure</b><br/>Unified Profile + Insights on Time Axis"]
        end
    end
    
    %% ============================================
    %% CONNECTIONS
    %% ============================================
    Identity --> Demographics
    Demographics --> UnifiedRecord
    
    StructuredProc --> StructuredInsights
    UnstructuredProc --> UnstructuredInsights
    
    %% Both insights are temporal on time axis
    StructuredInsights --> Historical
    UnstructuredInsights --> Historical
    Historical --> RealTime
    RealTime --> Trends
    
    %% Unified profile marries with temporal insights to create Dynamic Profile 360 Graph
    UnifiedRecord --> Nodes
    StructuredInsights --> Nodes
    UnstructuredInsights --> Nodes
    Historical --> Edges
    RealTime --> Edges
    Trends --> Edges
    
    Nodes --> GraphStructure
    Edges --> GraphStructure
    
    %% ============================================
    %% ENHANCED STYLING WITH SOFT COLORS
    %% ============================================
    classDef unifiedStyle fill:#81c784,stroke:#388e3c,stroke-width:2px,color:#000000,font-weight:bold
    classDef structuredStyle fill:#ffb74d,stroke:#f57c00,stroke-width:2px,color:#000000,font-weight:bold
    classDef unstructuredStyle fill:#ce93d8,stroke:#8e24aa,stroke-width:2px,color:#000000,font-weight:bold
    classDef timeStyle fill:#4dd0e1,stroke:#0097a7,stroke-width:2px,color:#000000,font-weight:bold
    classDef graphStyle fill:#ba68c8,stroke:#7b1fa2,stroke-width:3px,color:#ffffff,font-weight:bold
    
    class Identity,Demographics,UnifiedRecord unifiedStyle
    class StructuredProc,StructuredInsights structuredStyle
    class UnstructuredProc,UnstructuredInsights unstructuredStyle
    class Historical,RealTime,Trends timeStyle
    class Nodes,Edges,GraphStructure graphStyle
```

## 🔄 Detailed Process Flow

### **Phase 1: Data Ingestion into Data Cloud**

1. **Enterprise Sources** → Multiple systems feed data directly into Data Cloud

   - Salesforce CRM (Accounts, Contacts, Leads, Cases)

   - Marketing Cloud (Email, SMS, Push campaigns)

   - Website Analytics (Product views, cart, purchases)

   - Mobile App (Push notifications, in-app events)

   - WhatsApp Business API (Message engagement)

   - IoT Hub (Smart wearables & devices - Vehicle Telematics, Vitals & Health Parameters)

   - E-commerce Platform (Purchase history, preferences)

   - Social Media (Engagement, sentiment)

2. **Data Streams** → Real-time and batch data ingestion

   - Streaming connectors for real-time events

   - ETL processes for batch data

   - API integrations for on-demand data

### **Phase 2: Data Cloud Internal Processing**

#### **2.1 Data Harmonization**

- Schema mapping across different source systems

- Data normalization and standardization

- Field mapping and transformation

- Data quality validation

#### **2.2 Identity Resolution**

- Match records across multiple sources

- Link related records using:

  - Email addresses

  - Phone numbers

  - Device IDs

  - Social media IDs

  - Custom identifiers

- Create unified identity graph

#### **2.3 Unified Profile Creation**

- Single source of truth for each individual

- Merge demographic data from all sources

- Resolve conflicts and prioritize data

- Create Unified Individual record

### **Phase 3: Insights Creation**

#### **3.1 Unstructured Data Processing**

- **Processing Technologies**:

  - **NLP (Natural Language Processing)**: Sentiment analysis, entity extraction, topic modeling, intent detection

  - **OCR (Optical Character Recognition)**: Extract text from images, documents, scanned files

  - **Image Recognition**: Identify objects, scenes, activities in images

  - **Computer Vision**: Analyze visual content, detect patterns, extract insights from images/videos

- **Data Sources**:

  - Support case descriptions

  - Social media posts and comments

  - Product reviews

  - Chat transcripts

  - Images and photos

  - Documents and scanned files

  - Video content

- **Output**: **Unstructured Insights**

  - Sentiment (positive, negative, neutral)

  - Lifestyle (Active, Luxury Seeker, Adventurer, etc.)

  - Health Profile (Fit, Active, Hypertensive, etc.)

  - Purchase Intent (High, Medium, Low)

  - Topics of Interest

  - Behavioral Patterns

#### **3.2 Structured Data Processing**

- **Processing Methods**:

  - **Calculated Insights**: Aggregations, scores, metrics from structured data

  - **Predictive AI Models**: Machine learning models for predictions and classifications

- **Data Sources**:

  - Engagement metrics (email, SMS, WhatsApp, push, website)

  - Transaction data

  - Behavioral data

  - Demographic data

  - Historical patterns

- **Output**: **Structured Insights**

  - Lifetime Value (LTV)

  - Loyalty Tier (Bronze, Silver, Gold, Platinum)

  - Favourite Brand (Nike, Samsung, Bose, etc.)

  - Preferred Channel (Email, SMS, WhatsApp, Push)

  - Preferred Send Schedule (Morning, Afternoon, Evening, Lunch Time)

  - Engagement Scores

  - Risk Scores

  - Fitness Milestone Progression

#### **3.3 Temporal Insights on Time Axis**

- Both **Unstructured Insights** and **Structured Insights** are stored on a **Time Axis**

- **Historical Data**: Past 30 days, 90 days, 1 year, lifetime

- **Real-Time Data**: Last hour, last 24 hours, current state

- **Trend Analysis**: Changes over time, progression patterns, shifts in behavior

- Insights evolve and change over time, creating a temporal dimension

### **Phase 4: Profile 360 Graph Creation**

#### **4.1 Unified Profile Component**

- Demographics (name, age, location, contact info)

- Identity resolution results

- Device information

- Contact preferences

#### **4.2 Insights on Time Axis**

- **Historical Data**:

  - Past 30 days engagement

  - Past 90 days behavior

  - Past 1 year trends

  - Lifetime metrics

- **Real-Time Data**:

  - Last hour activity

  - Last 24 hours engagement

  - Current state snapshot

- **Trend Analysis**:

  - Engagement trend changes

  - Behavior pattern shifts

  - Milestone progression (e.g., Beginner → Intermediate → Advanced)

  - Sentiment shifts over time

#### **4.3 Dynamic Profile 360 Graph Structure**

- **Unified Profile**: Demographics, identity, contact information

- **Temporal Structured Insights**: Lifetime value, loyalty tier, favourite brand, preferred channel, preferred send schedule (all on time axis)

- **Temporal Unstructured Insights**: Sentiment, lifestyle, health profile, purchase intent (all on time axis)

- **Nodes**: Individual, Insights (structured & unstructured), Events, Relationships

- **Edges**: Temporal links (time-based), Causal links (cause-effect), Correlation links (related insights)

- **Result**: **Dynamic Profile 360 Graph** - Unified profile married with both structured and unstructured insights, all temporal on the time axis, creating a complete, evolving view of each individual

### **Phase 5: Heroku App Connection via MCP**

1. **MCP Server Connection**:

   - Configure MCP server (`salesforce-apis`)

   - Authenticate with credentials (Username/Password or OAuth)

   - Access MCP tools (query, describe, create)

2. **Access Profile 360 Graph**:

   - Query Unified Individual records

   - Retrieve insights (structured and unstructured)

   - Access time-series data

   - Get complete Profile 360 Graph view

### **Phase 6: Smart Audience Building & Segmentation**

1. **AI Agent**:

   - Natural language processing for segment requests

   - Example: "Create a segment of 5 most highly engaged individuals"

   - Translates to SOQL queries

2. **Segmentation Engine**:

   - Dynamic segment creation based on criteria:

     - Engagement scores

     - Behavioral patterns

     - Demographics

     - Insights (sentiment, lifestyle, health)

   - Multi-dimensional filtering

   - Real-time segment updates

3. **Criteria Builder**:

   - Combine multiple filters

   - Complex logic (AND/OR conditions)

   - Time-based criteria

### **Phase 7: Personalization Engine**

1. **Dynamic Prompt Generation**:

   - Extract from Profile 360 Graph:

     - Favorite Exercise (Treadmill, Yoga, CrossFit, etc.)

     - Favorite Brand (Nike, Samsung, Bose, etc.)

     - Favorite Destination (Singapore, Maldives, Paris, etc.)

     - Lifestyle Quotient (Active, Luxury Seeker, etc.)

     - Health Profile & Fitness Milestone

     - Current Sentiment

     - Upcoming Events

2. **Image Generation**:

   - **Gemini Nano Banana**: 

     - Character-consistent generation

     - Uses profile picture as reference

     - Single-step generation

   - **Replicate**: 

     - SDXL base image generation

     - Face-swap for true face matching

     - Two-step process for accuracy

3. **Content Generation**:

   - Promotional text overlay:

     - Health alerts (if health profile not "Fit")

     - Milestone offers (50% discount on premium subscription)

     - Congratulatory messages (milestone progression)

   - Dynamic links:

     - Vacation flight booking (if upcoming event is "vacation")

     - Guitar purchase discount (if hobby is "playing guitar")

   - Multi-line text wrapping

   - Brand integration (visible gadgets/apparel)

### **Phase 8: Messaging Engine & Channel Routing**

1. **Channel Router**:

   - Analyze Profile 360 Graph for channel preferences

   - Calculate engagement scores per channel:

     - Email engagement score

     - SMS engagement score

     - WhatsApp engagement score

     - Push engagement score

   - Select preferred channel (highest score)

2. **Content Formatting**:

   - **Email Engine**: HTML email with personalized content, images, offers

   - **SMS Engine**: Short-form personalized text messages

   - **WhatsApp Engine**: Rich media (images, videos) + text

   - **Push Engine**: Notification with personalized content

3. **Delivery**:

   - Route to preferred channel

   - Send via appropriate platform:

     - Email → Marketing Cloud

     - SMS → Mobile Studio

     - WhatsApp → Business API

     - Push → Mobile App

     - Website → Personalized banners

### **Phase 9: Feedback Loop**

- Engagement metrics from delivered content feed back into Data Cloud

- Updates Profile 360 Graph with new engagement data

- Continuous learning and optimization

- Real-time profile updates

## 📊 Key Components

### **Data Cloud - Internal Processing**

- **Data Harmonization**: Schema mapping, normalization, standardization

- **Identity Resolution**: Match and link records across sources

- **Unified Profile**: Single source of truth for each individual

- **Unstructured Processing**: NLP, sentiment analysis, entity extraction

- **Calculated Insights**: Aggregations, scores, metrics from structured data

- **Profile 360 Graph**: Unified profile + insights on time axis

### **Profile 360 Graph Structure**

- **Unified Profile**: Demographics, identity, contact info

- **Structured Insights**: Engagement metrics, behavioral patterns, calculated scores

- **Unstructured Insights**: Sentiment, topics, intents from text data

- **Time Axis**: Historical data, real-time data, trend analysis

- **Graph Nodes**: Individual, insights, events, relationships

- **Graph Edges**: Temporal, causal, and correlation links

### **Heroku App - MCP Integration**

- **MCP Server**: `salesforce-apis` protocol

- **Authentication**: Username/Password or OAuth

- **Tools**: Query, Describe, Create Salesforce objects

- **Access**: Profile 360 Graph via SOQL queries

### **Smart Audience Building**

- **AI Agent**: Natural language processing for segment requests

- **Segmentation Engine**: Dynamic segment creation with multi-dimensional filtering

- **Criteria Builder**: Complex logic for segment criteria

### **Personalization Engine**

- **Dynamic Prompts**: Context-aware prompt generation from Profile 360

- **Gemini**: Character-consistent image generation

- **Replicate**: Face-swap for accurate face matching

- **Content Generation**: Text, offers, links, overlays

### **Messaging Engine**

- **Channel Router**: Preferred channel detection based on engagement scores

- **Content Formatting**: Channel-specific content formatting

- **Multi-Channel Delivery**: Email, SMS, WhatsApp, Push, Website

## 🎯 Use Cases

1. **Hyper-Personalized Campaigns**: Generate unique images for each individual based on their complete Profile 360 Graph

2. **Milestone Celebrations**: Detect fitness progression from time-series data and send congratulatory offers

3. **Health Alerts**: Identify health risks from unstructured insights and route to appropriate channels

4. **Channel Optimization**: Automatically route to best-performing channel per individual based on engagement history

5. **Real-Time Personalization**: Update content based on latest insights from Profile 360 Graph

6. **Sentiment-Based Messaging**: Adjust messaging tone based on current sentiment from unstructured data processing

7. **Trend-Based Offers**: Identify behavior trends and offer relevant products/services

## 🔐 Security & Compliance

- **Data Cloud Security**: Enterprise-grade security for data ingestion and processing

- **MCP Authentication**: Secure credential management for Heroku app

- **Data Privacy**: Respects consent preferences per channel

- **GDPR Compliance**: Data Cloud handles privacy regulations

- **Secure APIs**: OAuth 2.0 for Salesforce connections

- **Identity Resolution**: Privacy-preserving matching algorithms

---

**Generated**: 2025-01-30

**Version**: v110

**Architecture**: Data Cloud-Centric + Profile 360 Graph + MCP + AI Personalization + Multi-Channel Delivery
