import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import io

# Page configuration
st.set_page_config(
    page_title="IMovie Marketing Strategy Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #E50914;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #564d4d;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    
    /* Enhanced metric styling */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2c3e50;
    }
    
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 2px solid #e0e0e0;
    }
    
    /* Different colors for different metric types */
    div[data-testid="column"]:nth-child(1) div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    div[data-testid="column"]:nth-child(1) div[data-testid="stMetricValue"],
    div[data-testid="column"]:nth-child(1) div[data-testid="stMetricLabel"] {
        color: white !important;
    }
    
    div[data-testid="column"]:nth-child(2) div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    div[data-testid="column"]:nth-child(2) div[data-testid="stMetricValue"],
    div[data-testid="column"]:nth-child(2) div[data-testid="stMetricLabel"] {
        color: white !important;
    }
    
    div[data-testid="column"]:nth-child(3) div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    div[data-testid="column"]:nth-child(3) div[data-testid="stMetricValue"],
    div[data-testid="column"]:nth-child(3) div[data-testid="stMetricLabel"] {
        color: white !important;
    }
    
    div[data-testid="column"]:nth-child(4) div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    }
    
    div[data-testid="column"]:nth-child(4) div[data-testid="stMetricValue"],
    div[data-testid="column"]:nth-child(4) div[data-testid="stMetricLabel"] {
        color: white !important;
    }
    
    div[data-testid="column"]:nth-child(5) div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    }
    
    div[data-testid="column"]:nth-child(5) div[data-testid="stMetricValue"],
    div[data-testid="column"]:nth-child(5) div[data-testid="stMetricLabel"] {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

# Title
st.markdown('<p class="main-header">🎬 IMovie Streaming Service</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">December 2025 Marketing Strategy Dashboard</p>', unsafe_allow_html=True)

# Sidebar for file upload
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/movie.png", width=100)
    st.title("📊 Dashboard Controls")
    
    st.markdown("---")
    st.subheader("📁 Upload Dataset")
    
    uploaded_file = st.file_uploader(
        "Upload your film dataset (CSV or XLSX)",
        type=['csv', 'xlsx'],
        help="Drag and drop or click to upload your dataset"
    )
    
    if uploaded_file:
        st.success("✅ File uploaded successfully!")

# Data loading and preprocessing function
@st.cache_data
def load_and_preprocess_data(file):
    """Load and preprocess the dataset"""
    try:
        # Read file based on extension
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        # Store original shape
        original_shape = df.shape
        
        # Convert date columns to datetime
        date_columns = ['Release_Date', 'Viewing_Month']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Remove rows with dates in 2026 or later
        if 'Release_Date' in df.columns:
            df = df[df['Release_Date'].dt.year < 2026]
        if 'Viewing_Month' in df.columns:
            df = df[df['Viewing_Month'].dt.year < 2026]
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values
        df = df.dropna(subset=['Film_Name'])
        
        # Convert numeric columns
        numeric_cols = ['Viewer_Rate', 'Number_of_Views']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove rows with missing critical values
        df = df.dropna(subset=numeric_cols)
        
        # Create additional features
        if 'Release_Date' in df.columns:
            df['Release_Year'] = df['Release_Date'].dt.year
            df['Release_Month'] = df['Release_Date'].dt.month
            df['Release_Month_Name'] = df['Release_Date'].dt.strftime('%B')
        
        if 'Viewing_Month' in df.columns:
            df['Viewing_Year'] = df['Viewing_Month'].dt.year
            df['Viewing_Month_Num'] = df['Viewing_Month'].dt.month
            df['Viewing_Month_Name'] = df['Viewing_Month'].dt.strftime('%B')
        
        # Calculate engagement score
        if 'Viewer_Rate' in df.columns and 'Number_of_Views' in df.columns:
            df['Engagement_Score'] = df['Viewer_Rate'] * np.log1p(df['Number_of_Views'])
        
        preprocessing_info = {
            'original_rows': original_shape[0],
            'original_cols': original_shape[1],
            'final_rows': df.shape[0],
            'final_cols': df.shape[1],
            'removed_rows': original_shape[0] - df.shape[0]
        }
        
        return df, preprocessing_info
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None

# Main application logic
if uploaded_file is not None:
    with st.spinner("🔄 Loading and preprocessing data..."):
        df, prep_info = load_and_preprocess_data(uploaded_file)
    
    if df is not None:
        st.session_state.data_loaded = True
        
        # Show preprocessing information
        with st.expander("ℹ️ Data Preprocessing Summary", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Original Rows", prep_info['original_rows'])
            col2.metric("Final Rows", prep_info['final_rows'])
            col3.metric("Removed Rows", prep_info['removed_rows'], delta=f"-{prep_info['removed_rows']}")
            col4.metric("Total Columns", prep_info['final_cols'])
            
            st.info("✅ Removed all entries with dates in 2026 or later")
            st.info("✅ Removed duplicate entries")
            st.info("✅ Handled missing values")
        
        # Create tabs for different sections
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Overview", 
            "🎯 December 2025 Strategy", 
            "📈 Advanced Analytics",
            "🎭 Category & Language Insights",
            "⭐ Performance Analysis",
            "💡 Recommendations"
        ])
        
        # TAB 1: OVERVIEW
        with tab1:
            st.header("📊 Dataset Overview")
            
            # Key Metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Total Films", len(df))
            with col2:
                st.metric("Total Views", f"{df['Number_of_Views'].sum():,.0f}")
            with col3:
                st.metric("Avg Rating", f"{df['Viewer_Rate'].mean():.2f}/5")
            with col4:
                st.metric("Categories", df['Category'].nunique())
            with col5:
                st.metric("Languages", df['Language'].nunique())
            
            st.markdown("---")
            
            # Two column layout
            col1, col2 = st.columns(2)
            
            with col1:
                # Category Distribution
                category_counts = df['Category'].value_counts()
                fig_category = px.pie(
                    values=category_counts.values,
                    names=category_counts.index,
                    title="Distribution by Category",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_category.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_category, use_container_width=True)
            
            with col2:
                # Language Distribution
                language_counts = df['Language'].value_counts().head(10)
                fig_language = px.bar(
                    x=language_counts.values,
                    y=language_counts.index,
                    orientation='h',
                    title="Top 10 Languages",
                    labels={'x': 'Number of Films', 'y': 'Language'},
                    color=language_counts.values,
                    color_continuous_scale='viridis'
                )
                st.plotly_chart(fig_language, use_container_width=True)
            
            # Views and Ratings over time
            col1, col2 = st.columns(2)
            
            with col1:
                if 'Viewing_Month_Name' in df.columns:
                    monthly_views = df.groupby('Viewing_Month_Name')['Number_of_Views'].sum().reindex([
                        'January', 'February', 'March', 'April', 'May', 'June',
                        'July', 'August', 'September', 'October', 'November', 'December'
                    ])
                    fig_views = px.line(
                        x=monthly_views.index,
                        y=monthly_views.values,
                        title="Total Views by Month",
                        labels={'x': 'Month', 'y': 'Total Views'},
                        markers=True
                    )
                    fig_views.update_traces(line_color='#E50914', line_width=3)
                    st.plotly_chart(fig_views, use_container_width=True)
            
            with col2:
                # Average rating by category
                avg_rating = df.groupby('Category')['Viewer_Rate'].mean().sort_values(ascending=False)
                fig_rating = px.bar(
                    x=avg_rating.values,
                    y=avg_rating.index,
                    orientation='h',
                    title="Average Viewer Rating by Category",
                    labels={'x': 'Average Rating', 'y': 'Category'},
                    color=avg_rating.values,
                    color_continuous_scale='RdYlGn'
                )
                st.plotly_chart(fig_rating, use_container_width=True)
        
        # TAB 2: DECEMBER 2025 STRATEGY
        with tab2:
            st.header("🎯 December 2025 Marketing Strategy Insights")
            
            # Filter December data
            december_df = df[df['Viewing_Month_Name'] == 'December'] if 'Viewing_Month_Name' in df.columns else df
            
            st.subheader("🎄 December Performance Highlights")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("December Films", len(december_df))
            with col2:
                st.metric("December Views", f"{december_df['Number_of_Views'].sum():,.0f}")
            with col3:
                st.metric("Avg December Rating", f"{december_df['Viewer_Rate'].mean():.2f}")
            with col4:
                engagement = december_df['Engagement_Score'].mean() if 'Engagement_Score' in december_df.columns else 0
                st.metric("Engagement Score", f"{engagement:.2f}")
            
            st.markdown("---")
            
            # December category performance
            col1, col2 = st.columns(2)
            
            with col1:
                dec_category = december_df.groupby('Category').agg({
                    'Number_of_Views': 'sum',
                    'Viewer_Rate': 'mean'
                }).sort_values('Number_of_Views', ascending=False)
                
                fig_dec_cat = px.bar(
                    dec_category,
                    x=dec_category.index,
                    y='Number_of_Views',
                    title="December Views by Category",
                    labels={'Number_of_Views': 'Total Views', 'index': 'Category'},
                    color='Viewer_Rate',
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig_dec_cat, use_container_width=True)
                
                # Top recommendation
                top_category = dec_category.index[0]
                st.success(f"💡 **Strategy Insight:** Focus marketing on **{top_category}** films for December!")
            
            with col2:
                # December language performance
                dec_language = december_df.groupby('Language')['Number_of_Views'].sum().sort_values(ascending=False).head(8)
                
                fig_dec_lang = px.funnel(
                    y=dec_language.index,
                    x=dec_language.values,
                    title="December Top Languages (Funnel View)",
                    labels={'x': 'Views', 'y': 'Language'}
                )
                st.plotly_chart(fig_dec_lang, use_container_width=True)
            
            # High engagement films for December
            st.subheader("🌟 Recommended Films for December 2025 Campaign")
            
            if 'Engagement_Score' in december_df.columns:
                top_films = december_df.nlargest(10, 'Engagement_Score')[
                    ['Film_Name', 'Category', 'Language', 'Viewer_Rate', 'Number_of_Views', 'Engagement_Score']
                ]
                
                fig_top = px.scatter(
                    top_films,
                    x='Number_of_Views',
                    y='Viewer_Rate',
                    size='Engagement_Score',
                    color='Category',
                    hover_data=['Film_Name', 'Language'],
                    title="Top 10 Films by Engagement Score for December Marketing",
                    labels={'Number_of_Views': 'Total Views', 'Viewer_Rate': 'Rating'}
                )
                st.plotly_chart(fig_top, use_container_width=True)
                
                st.dataframe(
                    top_films.style.background_gradient(subset=['Engagement_Score'], cmap='YlOrRd'),
                    use_container_width=True
                )
        
        # TAB 3: ADVANCED ANALYTICS
        with tab3:
            st.header("📈 Advanced Analytics")
            
            # Correlation Analysis
            st.subheader("🔗 Correlation Analysis")
            
            numeric_df = df.select_dtypes(include=[np.number])
            corr_matrix = numeric_df.corr()
            
            fig_corr = px.imshow(
                corr_matrix,
                title="Correlation Heatmap",
                color_continuous_scale='RdBu',
                aspect='auto'
            )
            st.plotly_chart(fig_corr, use_container_width=True)
            
            st.markdown("---")
            
            # Trend Analysis
            col1, col2 = st.columns(2)
            
            with col1:
                # Views vs Rating scatter
                fig_scatter = px.scatter(
                    df,
                    x='Viewer_Rate',
                    y='Number_of_Views',
                    color='Category',
                    size='Number_of_Views',
                    title="Viewer Rating vs Number of Views",
                    labels={'Viewer_Rate': 'Rating', 'Number_of_Views': 'Views'},
                    hover_data=['Film_Name']
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
            
            with col2:
                # Box plot for ratings by category
                fig_box = px.box(
                    df,
                    x='Category',
                    y='Viewer_Rate',
                    color='Category',
                    title="Rating Distribution by Category",
                    labels={'Viewer_Rate': 'Rating'}
                )
                st.plotly_chart(fig_box, use_container_width=True)
            
            # Engagement score analysis
            if 'Engagement_Score' in df.columns:
                st.subheader("💎 Engagement Score Analysis")
                
                engagement_by_cat = df.groupby('Category')['Engagement_Score'].mean().sort_values(ascending=False)
                
                fig_engage = px.bar(
                    x=engagement_by_cat.index,
                    y=engagement_by_cat.values,
                    title="Average Engagement Score by Category",
                    labels={'x': 'Category', 'y': 'Avg Engagement Score'},
                    color=engagement_by_cat.values,
                    color_continuous_scale='turbo'
                )
                st.plotly_chart(fig_engage, use_container_width=True)
        
        # TAB 4: CATEGORY & LANGUAGE INSIGHTS
        with tab4:
            st.header("🎭 Category & Language Deep Dive")
            
            # Interactive filters
            col1, col2 = st.columns(2)
            with col1:
                selected_categories = st.multiselect(
                    "Select Categories",
                    options=df['Category'].unique(),
                    default=df['Category'].unique()[:3]
                )
            with col2:
                selected_languages = st.multiselect(
                    "Select Languages",
                    options=df['Language'].unique(),
                    default=df['Language'].unique()[:5]
                )
            
            filtered_df = df[
                (df['Category'].isin(selected_categories)) & 
                (df['Language'].isin(selected_languages))
            ]
            
            st.info(f"Showing data for {len(filtered_df)} films")
            
            # Category-Language cross analysis
            st.subheader("🔄 Category-Language Cross Analysis")
            
            cross_tab = pd.crosstab(filtered_df['Category'], filtered_df['Language'], 
                                   values=filtered_df['Number_of_Views'], aggfunc='sum')
            
            fig_heatmap = px.imshow(
                cross_tab,
                title="Views Heatmap: Category vs Language",
                labels=dict(x="Language", y="Category", color="Total Views"),
                color_continuous_scale='YlOrRd',
                aspect='auto'
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
            # Performance metrics by selection
            col1, col2 = st.columns(2)
            
            with col1:
                category_performance = filtered_df.groupby('Category').agg({
                    'Number_of_Views': 'sum',
                    'Viewer_Rate': 'mean',
                    'Film_Name': 'count'
                }).round(2)
                category_performance.columns = ['Total Views', 'Avg Rating', 'Film Count']
                
                st.subheader("📊 Category Performance")
                st.dataframe(category_performance.style.background_gradient(cmap='Blues'), use_container_width=True)
            
            with col2:
                language_performance = filtered_df.groupby('Language').agg({
                    'Number_of_Views': 'sum',
                    'Viewer_Rate': 'mean',
                    'Film_Name': 'count'
                }).round(2)
                language_performance.columns = ['Total Views', 'Avg Rating', 'Film Count']
                
                st.subheader("📊 Language Performance")
                st.dataframe(language_performance.style.background_gradient(cmap='Greens'), use_container_width=True)
        
        # TAB 5: PERFORMANCE ANALYSIS
        with tab5:
            st.header("⭐ Performance Analysis")
            
            # Top and Bottom performers
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🏆 Top 10 Performing Films")
                top_10 = df.nlargest(10, 'Number_of_Views')[
                    ['Film_Name', 'Category', 'Viewer_Rate', 'Number_of_Views']
                ]
                
                fig_top10 = px.bar(
                    top_10,
                    x='Number_of_Views',
                    y='Film_Name',
                    orientation='h',
                    color='Viewer_Rate',
                    title="Top 10 Films by Views",
                    color_continuous_scale='Greens'
                )
                st.plotly_chart(fig_top10, use_container_width=True)
            
            with col2:
                st.subheader("⭐ Highest Rated Films")
                top_rated = df.nlargest(10, 'Viewer_Rate')[
                    ['Film_Name', 'Category', 'Viewer_Rate', 'Number_of_Views']
                ]
                
                fig_rated = px.bar(
                    top_rated,
                    x='Viewer_Rate',
                    y='Film_Name',
                    orientation='h',
                    color='Number_of_Views',
                    title="Top 10 Highest Rated Films",
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig_rated, use_container_width=True)
            
            # Performance quadrant analysis
            st.subheader("📍 Performance Quadrant Analysis")
            
            median_views = df['Number_of_Views'].median()
            median_rating = df['Viewer_Rate'].median()
            
            df['Quadrant'] = 'Low Performance'
            df.loc[(df['Number_of_Views'] >= median_views) & (df['Viewer_Rate'] >= median_rating), 'Quadrant'] = 'Star Performers'
            df.loc[(df['Number_of_Views'] >= median_views) & (df['Viewer_Rate'] < median_rating), 'Quadrant'] = 'High Views, Low Rating'
            df.loc[(df['Number_of_Views'] < median_views) & (df['Viewer_Rate'] >= median_rating), 'Quadrant'] = 'Hidden Gems'
            
            fig_quadrant = px.scatter(
                df,
                x='Number_of_Views',
                y='Viewer_Rate',
                color='Quadrant',
                size='Number_of_Views',
                hover_data=['Film_Name', 'Category'],
                title="Film Performance Quadrants",
                color_discrete_map={
                    'Star Performers': 'green',
                    'High Views, Low Rating': 'orange',
                    'Hidden Gems': 'blue',
                    'Low Performance': 'red'
                }
            )
            
            fig_quadrant.add_hline(y=median_rating, line_dash="dash", line_color="gray")
            fig_quadrant.add_vline(x=median_views, line_dash="dash", line_color="gray")
            
            st.plotly_chart(fig_quadrant, use_container_width=True)
            
            # Quadrant counts
            quadrant_counts = df['Quadrant'].value_counts()
            col1, col2, col3, col4 = st.columns(4)
            
            for idx, (quadrant, count) in enumerate(quadrant_counts.items()):
                with [col1, col2, col3, col4][idx]:
                    st.metric(quadrant, count)
        
        # TAB 6: RECOMMENDATIONS
        with tab6:
            st.header("💡 Strategic Recommendations for December 2025")
            
            # Generate insights
            december_df = df[df['Viewing_Month_Name'] == 'December'] if 'Viewing_Month_Name' in df.columns else df
            
            top_december_category = december_df.groupby('Category')['Number_of_Views'].sum().idxmax()
            top_december_language = december_df.groupby('Language')['Number_of_Views'].sum().idxmax()
            avg_december_rating = december_df['Viewer_Rate'].mean()
            
            # Best performing time insights
            if 'Viewing_Month_Name' in df.columns:
                monthly_performance = df.groupby('Viewing_Month_Name')['Number_of_Views'].sum()
                best_month = monthly_performance.idxmax()
                december_rank = monthly_performance.rank(ascending=False)['December'] if 'December' in monthly_performance.index else 'N/A'
            
            st.markdown("### 🎯 Key Marketing Recommendations")
            
            recommendations = [
                {
                    "title": "🎬 Focus on Top Category",
                    "description": f"Prioritize **{top_december_category}** content in December campaigns. This category has historically performed best during this month.",
                    "action": f"Allocate 40% of marketing budget to promote {top_december_category} films"
                },
                {
                    "title": "🌍 Language Strategy",
                    "description": f"**{top_december_language}** language content shows highest engagement in December.",
                    "action": f"Create targeted campaigns for {top_december_language}-speaking audiences"
                },
                {
                    "title": "⭐ Quality Focus",
                    "description": f"December average rating is **{avg_december_rating:.2f}/10**. Focus on high-quality content.",
                    "action": "Promote films with ratings above 7.0 to maintain brand reputation"
                },
                {
                    "title": "📱 Engagement Optimization",
                    "description": "Star Performer films show best ROI with high views and ratings.",
                    "action": "Feature 'Star Performer' quadrant films prominently on homepage"
                }
            ]
            
            for i, rec in enumerate(recommendations, 1):
                with st.expander(f"**Recommendation {i}: {rec['title']}**", expanded=True):
                    st.write(rec['description'])
                    st.success(f"**Action Item:** {rec['action']}")
            
            st.markdown("---")
            
            # Content mix recommendation
            st.markdown("### 📊 Recommended Content Mix for December 2025")
            
            category_mix = december_df.groupby('Category')['Number_of_Views'].sum()
            category_mix_pct = (category_mix / category_mix.sum() * 100).round(1)
            
            fig_mix = px.pie(
                values=category_mix_pct.values,
                names=category_mix_pct.index,
                title="Recommended Category Distribution for December Marketing",
                hole=0.4
            )
            fig_mix.update_traces(textposition='outside', textinfo='percent+label')
            st.plotly_chart(fig_mix, use_container_width=True)
            
            # Marketing calendar
            st.markdown("### 📅 December 2025 Marketing Calendar")
            
            calendar_data = {
                'Week': ['Week 1 (Dec 1-7)', 'Week 2 (Dec 8-14)', 'Week 3 (Dec 15-21)', 'Week 4 (Dec 22-31)'],
                'Focus': [
                    f'Launch {top_december_category} campaign',
                    'Mid-month engagement push',
                    'Holiday season special promotions',
                    'Year-end celebration content'
                ],
                'Content Type': [
                    'New releases announcement',
                    'User-generated content campaign',
                    'Gift subscription promotions',
                    'New Year preview teasers'
                ],
                'Budget Allocation': ['30%', '25%', '25%', '20%']
            }
            
            calendar_df = pd.DataFrame(calendar_data)
            st.dataframe(calendar_df, use_container_width=True, hide_index=True)
            
            # Final success metrics
            st.markdown("### 🎯 Success Metrics to Track")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.info("""
                **Engagement Metrics**
                - View count increase
                - Watch time duration
                - Completion rate
                """)
            
            with col2:
                st.info("""
                **Acquisition Metrics**
                - New subscribers
                - Trial conversions
                - Referral signups
                """)
            
            with col3:
                st.info("""
                **Retention Metrics**
                - Churn rate
                - Active users
                - Content satisfaction
                """)
        
        # Data export option
        st.markdown("---")
        st.subheader("📥 Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Processed Data as CSV",
                data=csv,
                file_name="imovie_processed_data.csv",
                mime="text/csv"
            )
        
        with col2:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Processed Data', index=False)
            
            st.download_button(
                label="Download Processed Data as Excel",
                data=buffer.getvalue(),
                file_name="imovie_processed_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

else:
    # Welcome screen
    st.markdown("""
        <div style='text-align: center; padding: 50px;'>
            <h2>👋 Welcome to IMovie Marketing Dashboard</h2>
            <p style='font-size: 1.2rem; color: #666;'>
                Please upload your film dataset using the sidebar to get started.
            </p>
            <p style='font-size: 1rem; color: #888;'>
                Supported formats: CSV, XLSX
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            ### 📊 Comprehensive Analytics
            - Dataset overview and statistics
            - Performance metrics
            - Trend analysis
        """)
    
    with col2:
        st.markdown("""
            ### 🎯 Strategic Insights
            - December 2025 strategy
            - Content recommendations
            - Marketing calendar
        """)
    
    with col3:
        st.markdown("""
            ### 📈 Interactive Visualizations
            - Real-time charts
            - Customizable filters
            - Export capabilities
        """)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🎬 IMovie Marketing Strategy Dashboard | December 2025</p>
        <p style='font-size: 0.9rem;'>Designed for managerial insights and data-driven decision making</p>
    </div>

""", unsafe_allow_html=True)
