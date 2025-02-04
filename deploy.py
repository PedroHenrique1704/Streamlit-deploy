import pandas            as pd
import streamlit         as st
import seaborn           as sns
import matplotlib.pyplot as plt
from PIL                 import Image
from io                  import BytesIO
import io
import base64




    # Configs streamlit

st.set_page_config(page_title='Análise Bancaria',
                       page_icon='./img/pag_icon.png',
                       layout="wide",
                       initial_sidebar_state='expanded')

    # Deixando os gráficos mais bonitos

custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)



    # CSS

# Arquivo css

def carregar_css(arquivo_css):
    with open(arquivo_css) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

carregar_css("./css/estilo.css")

     # Selectbox sem rótulo

def css_rotulo():
    st.markdown(
        """
        <style>
        /* Ocultar o rótulo da selectbox */
        .stSelectbox label {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

css_rotulo()


    # Funções



# Função para ler os dados
@st.cache_data
def load_data(file_data):
    try:
        return pd.read_csv(file_data, sep=';')
    except:
        return pd.read_excel(file_data)

# Função para filtrar baseado na multiseleção de categorias
@st.cache_data
def multiselect_filter(relatorio, col, selecionados):
    if 'all' in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)

# Função para converter o df para csv
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# Função para converter o df para excel
@st.cache_data
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data


    # Datasets

bank_raw = pd.read_csv('./data/input/bank-additional-full.csv', sep=';')
bank = bank_raw.copy()

    # Streamlit


st.markdown("<h1 style='text-align: center;'>Análise Bancaria</h1>", unsafe_allow_html=True)


# Imagem
image = Image.open("./img/icon.png")
st.sidebar.image(image)


# Botão para carregar arquivo na aplicação
st.sidebar.write("## Suba o arquivo de dados")
data_file_1 = st.sidebar.file_uploader("Marketing bancario ficticio", type = ['csv','xlsx'])


# Verifica se há conteúdo carregado na aplicação
if (data_file_1 is not None):
        bank_raw = load_data(data_file_1)
        bank = bank_raw.copy()

        df_csv = convert_df(bank)
        df_xlsx = to_excel(bank)

        st.markdown("<h2 style='text-align: center;'>Banco de dados bruto</h2>", unsafe_allow_html=True)

        st.write(bank_raw.head())

        with st.sidebar.form(key='my_form'):

            # SELECIONA O TIPO DE GRÁFICO
            graph_type = st.radio('Tipo de gráfico:', ('Barras', 'Pizza'))

            # IDADES
            max_age = int(bank.age.max())
            min_age = int(bank.age.min())
            idades = st.slider(label='Idade', 
                                            min_value = min_age,
                                            max_value = max_age, 
                                            value = (min_age, max_age),
                                            step = 1)


            st.markdown("*Conjuntos vazios serão consideramos como All*")

            # PROFISSÕES
            jobs_list = bank.job.unique().tolist()
            jobs_list.append('all')
            jobs_selected =  st.multiselect("Profissão", jobs_list, ['all'])

            # ESTADO CIVIL
            marital_list = bank.marital.unique().tolist()
            marital_list.append('all')
            marital_selected =  st.multiselect("Estado civil", marital_list, ['all'])

            # DEFAULT?
            default_list = bank.default.unique().tolist()
            default_list.append('all')
            default_selected =  st.multiselect("Default", default_list, ['all'])

            
            # TEM FINANCIAMENTO IMOBILIÁRIO?
            housing_list = bank.housing.unique().tolist()
            housing_list.append('all')
            housing_selected =  st.multiselect("Tem financiamento imob?", housing_list, ['all'])

            
            # TEM EMPRÉSTIMO?
            loan_list = bank.loan.unique().tolist()
            loan_list.append('all')
            loan_selected =  st.multiselect("Tem empréstimo?", loan_list, ['all'])

            
            # MEIO DE CONTATO?
            contact_list = bank.contact.unique().tolist()
            contact_list.append('all')
            contact_selected =  st.multiselect("Meio de contato", contact_list, ['all'])

            
            # MÊS DO CONTATO
            month_list = bank.month.unique().tolist()
            month_list.append('all')
            month_selected =  st.multiselect("Mês do contato", month_list, ['all'])

            
            # DIA DA SEMANA
            day_of_week_list = bank.day_of_week.unique().tolist()
            day_of_week_list.append('all')
            day_of_week_selected =  st.multiselect("Dia da semana", day_of_week_list, ['all'])


            # Botão de envio DENTRO do formulário
            submit_button = st.form_submit_button(label='Aplicar')

            # Verifica e substitui listas vazias por ['all']
            if submit_button:
                if not jobs_selected:
                    jobs_selected = ['all']
                if not marital_selected:
                    marital_selected = ['all']
                if not default_selected:
                    default_selected = ['all']
                if not housing_selected:
                    housing_selected = ['all']
                if not loan_selected:
                    loan_selected = ['all']
                if not contact_selected:
                    contact_selected = ['all']
                if not month_selected:
                    month_selected = ['all']
                if not day_of_week_selected:
                    day_of_week_selected = ['all']  

                # Encadeamento de métodos para filtrar a seleção
                bank = (bank.query("age >= @idades[0] and age <= @idades[1]")
                            .pipe(multiselect_filter, 'job', jobs_selected)
                            .pipe(multiselect_filter, 'marital', marital_selected)
                            .pipe(multiselect_filter, 'default', default_selected)
                            .pipe(multiselect_filter, 'housing', housing_selected)
                            .pipe(multiselect_filter, 'loan', loan_selected)
                            .pipe(multiselect_filter, 'contact', contact_selected)
                            .pipe(multiselect_filter, 'month', month_selected)
                            .pipe(multiselect_filter, 'day_of_week', day_of_week_selected)
                )

                df_csv = convert_df(bank)
                df_xlsx = to_excel(bank)


        
        # Dados filtrados
        st.markdown("<h2 style='text-align: center;'>Banco de dados filtrado</h2>", unsafe_allow_html=True)

        st.write(bank.head())
        st.write('\n')
        

        # Botão de download dados filtrados



        col_vazio, col1, col2, col3= st.columns([0.19,1,1,1])
        
        

        with col1:

        
            
            st.download_button(
                label='📥 Download tabela filtrada em EXCEL',
                data=df_xlsx,
                file_name= 'bank_filtered.xlsx')
        
        with col2:

            
            st.download_button(
                label="📥 Download tabela filtrada em CSV",
                data= df_csv,
                file_name='df_csv.csv',
                mime='text/csv',
        )
            
                 
                # PLOT


       # Definindo a paleta de cores e o mapping

        paleta = 'pastel' 

        label_mapping = {
            'no': 'Adimplente',
            'yes': 'Inadimplente'
        }

        # Configuração da figura
        fig, ax = plt.subplots(1, 2, figsize=(10, 5)) 

        # Proporção de valores originais
        bank_raw_target_perc = bank_raw['y'].value_counts(normalize=True).to_frame(name='percent') * 100
        bank_raw_target_perc = bank_raw_target_perc.sort_index()

        # Gráfico de barras
        if graph_type == "Barras":

            # Alterar os índices para 'Adimplente' e 'Inadimplente'
            bank_raw_target_perc.index = bank_raw_target_perc.index.map({'no': 'Adimplente', 'yes': 'Inadimplente'})

            # Gráfico 1 (bruto)
            sns.barplot(x=bank_raw_target_perc.index,
                        y=bank_raw_target_perc['percent'],  # Nome correto da coluna
                        ax=ax[0],
                        palette=paleta)
            
            # Arredondar os valores e adicionar o símbolo %
            ax[0].bar_label(ax[0].containers[0], fmt='%.2f%%')
            ax[0].bar_label(ax[0].containers[1], fmt='%.2f%%')
            ax[0].set_title('Dados Brutos', fontweight="bold", pad=20)
            ax[0].set_ylabel('Percentual de pessoas inadimplentes')  # Alterar o rótulo do eixo Y
            ax[0].set_xlabel('')  # Alterar o rótulo do eixo X
            
            # Proporção de valores filtrados
            bank_target_perc = bank['y'].value_counts(normalize=True).to_frame(name='percent') * 100
            bank_target_perc = bank_target_perc.rename(index=label_mapping).reindex(label_mapping.values())  # Reordena com o mapeamento

            # Gráfico 2 (filtrado)
            sns.barplot(x=bank_target_perc.index,
                        y=bank_target_perc['percent'],  # Nome correto da coluna
                        ax=ax[1],
                        palette=paleta)
            
            ax[1].bar_label(ax[1].containers[0], fmt='%.2f%%')
            ax[1].bar_label(ax[1].containers[1], fmt='%.2f%%')
            ax[1].set_title('Dados Filtrados', fontweight="bold", pad=20)
            ax[1].set_ylabel('Percentual de pessoas inadimplentes')  # Alterar o rótulo do eixo Y
            ax[1].set_xlabel('')  # Alterar o rótulo do eixo X


            



        elif graph_type == "Pizza":
            # Alterar os índices para 'Adimplente' e 'Inadimplente'
            bank_raw_target_perc.index = bank_raw_target_perc.index.map({'no': 'Adimplente', 'yes': 'Inadimplente'})

            # Gráfico dos dados brutos
            ax[0].pie(bank_raw_target_perc['percent'], 
                    labels=bank_raw_target_perc.index, 
                    autopct='%.2f%%',  # Arredondar os valores com duas casas decimais e adicionar o símbolo %
                    colors=sns.color_palette(paleta), 
                    startangle=90)
            ax[0].set_title('Dados Brutos', fontweight="bold")

            # Proporção de valores filtrados
            bank_target_perc = bank['y'].value_counts(normalize=True).to_frame(name='percent') * 100
            bank_target_perc = bank_target_perc.rename(index=label_mapping).reindex(label_mapping.values())  # Reordena com o mapeamento

            # Gráfico dos dados filtrados
            ax[1].pie(bank_target_perc['percent'], 
                    labels=bank_target_perc.index, 
                    autopct='%.2f%%',  # Arredondar os valores com duas casas decimais e adicionar o símbolo %
                    colors=sns.color_palette(paleta), 
                    startangle=90)
            ax[1].set_title('Dados Filtrados', fontweight="bold")


        plt.savefig("grafico.png")
        plt.close(fig)  # Fecha a figura para liberar memória

        with col3:

            # Cria o botão de download
            with open("grafico.png", "rb") as file:
                st.download_button(
                    label="📊 Download do gráfico como PNG",
                    data=file,
                    file_name='grafico.png',
                    mime='image/png'
                )

        # Título e exibição no Streamlit

        st.pyplot(fig)



elif (data_file_1 is None):

    st.markdown("<h3 style='text-align: center;'>Adicione um banco de dados para começar</h3>", unsafe_allow_html=True)

    image = Image.open("./img/icon.png")
    st.image(image)