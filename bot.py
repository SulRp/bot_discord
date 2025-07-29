import asyncio
import discord
from discord.ext import commands
from discord.ui import Button, Modal, TextInput, View, Select, button
from discord import ButtonStyle, app_commands, Interaction, Embed
import mysql.connector
from datetime import datetime, timezone, timedelta
import random

# Configurações
TOKEN = 'Seu token'
PREFIX = '/'
intents = discord.Intents.all()
GUILD_ID =   # ID do servidor

######################
# -= Cargos Staff =- #
######################
Leonne = # ID do usuário que irá cuidar do bot(pode alterar o nome para o seu) Linhas 18 e 413
Owner = # ID do cargo de dono
Admin = # ID do cargo de administrador
Mod = # ID do cargo de moderador
Suporte = # ID do cargo de suporte
Auxiliar = # ID do cargo de auxiliar
Equipe = # ID do cargo de equipe

####################
# -= Cargos Adv =- #
####################

AdvS1 = # ID do cargo Advertência Staff 1
AdvS2 = # ID do cargo Advertência Staff 2
AdvV = # ID do cargo Advertência Verbal
Adv1 = # ID do cargo Advertência 1
Adv2 = # ID do cargo Advertência 2
Ban = # ID do cargo de banimento

################
# -= Canais =- #
################

Advertencias = # ID do canal de advertências
Remocao = # ID do canal de remoção
Sorteio = # ID do canal de sorteio
Postar = # ID do canal de postar
Att = # ID do canal de atualização
FeedC = # ID do canal de feedback por chamadas
FeedT = # ID do canal de feedback por tickets

####################
# -= Categorias =- #
####################

SorteioC = # ID da categoria de sorteio

##############
# -= Null =- #
##############

def connect_db():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="nome_do_banco",
        port=3306
    )

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Comandos de barra sincronizados: {len(synced)}")
    except Exception as e:
        print(f"Erro ao sincronizar comandos: {e}")


###################
# -= Sugestões =- #
###################

@bot.tree.command(name="sugerir", description="Usado para sugerir uma ideia", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(texto="Sua sugestão")
async def sugerir_command(interaction: discord.Interaction, texto: str):
    if interaction.channel.id != 1354778355605442579:
        await interaction.response.send_message("❌ Este comando só pode ser usado no canal de sugestões.", ephemeral=True)
        return
    canal_sugestao = bot.get_channel(1218197732322185237)
    if canal_sugestao:
        embed = discord.Embed(title="Nova Sugestão", description=texto, color=discord.Color.blue())
        embed.set_author(name=interaction.user.name)
        mensagem = await canal_sugestao.send(embed=embed)
        await mensagem.add_reaction('✅')
        await mensagem.add_reaction('❌')
    await interaction.response.send_message("Sugestão enviada com sucesso!", ephemeral=True)

#########################
# -= Liberar Usuário =- #
#########################

@bot.tree.command(name="lib", description="Usar para entregar algum cargo ao usuário", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(usuario="Usuário", cargo="Cargo")
async def lib_command(interaction: discord.Interaction, usuario: discord.Member, cargo: discord.Role):
    await usuario.add_roles(cargo)
    await interaction.response.send_message(f"Cargo '{cargo.name}' adicionado a {usuario.display_name}.", ephemeral=True)

#####################
# -= Criar Embed =- #
#####################

@bot.tree.command(name="end", description="Cria uma mensagem em formato de caixa", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(mensagem="Texto a ser exibido")
async def end_command(interaction: discord.Interaction, mensagem: str):
    embed = discord.Embed(description=mensagem, color=discord.Color.blue())
    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("Mensagem enviada.", ephemeral=True)

###############
# -= Ajuda =- #
###############

async def mostrar_lista_comandos(interaction: discord.Interaction):
    embed = discord.Embed(title="📘 Lista de Comandos", color=discord.Color.blue())

    comandos_ordenados = sorted(bot.tree.get_commands(guild=discord.Object(id=GUILD_ID)), key=lambda cmd: cmd.name)

    for comando in comandos_ordenados:
        nome = f"/{comando.name}"
        desc = comando.description or "Sem descrição"
        embed.add_field(name=nome, value=desc, inline=False)

    embed.set_footer(text="Midnight RP © Todos os direitos reservados.")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="ajuda", description="Mostra os comandos disponíveis", guild=discord.Object(id=GUILD_ID))
async def ajuda_command(interaction: discord.Interaction):
    await mostrar_lista_comandos(interaction)

###############################
# -= Adicionar Advertência =- #
###############################

@bot.tree.command(name="advertir", description="Dar uma advertência a um usuário", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(usuario="Usuário a ser advertido", motivo="Motivo da advertência", observacao="Observação adicional (opcional)")
async def advertir_command(interaction: discord.Interaction, usuario: discord.Member, motivo: str, observacao: str = None):
    permitted_roles = [Owner, Admin, Mod]
    if not any(role.id in permitted_roles for role in interaction.user.roles):
        await interaction.response.send_message("⛔ Você não tem permissão para usar este comando.", ephemeral=True)
        return

    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM advertencias
        WHERE user_id = %s AND removida = FALSE
        ORDER BY data DESC
    """, (usuario.id,))
    advertencias_ativas = cursor.fetchall()
    cursor.close()
    conn.close()

    from datetime import datetime, timedelta
    hoje = datetime.utcnow()

    tipos_ativos = []
    for adv in advertencias_ativas:
        tipo = adv['tipo']
        validade = adv.get('validade')
        if tipo in ["Adv1", "Adv2"]:
            if validade is None or datetime.strptime(validade, "%Y-%m-%d %H:%M:%S") >= hoje:
                tipos_ativos.append(tipo)
        else:
            tipos_ativos.append(tipo)

    tipo_novo = "AdvV"
    if "AdvV" in tipos_ativos and "Adv1" not in tipos_ativos:
        tipo_novo = "Adv1"
    elif "Adv1" in tipos_ativos and "Adv2" not in tipos_ativos:
        tipo_novo = "Adv2"
    elif "Adv2" in tipos_ativos:
        tipo_novo = "Adv3"

    validade = None
    if tipo_novo in ["Adv1", "Adv2"]:
        validade = hoje + timedelta(days=30)

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO advertencias (user_id, author_id, motivo, observacao, tipo, validade)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (usuario.id, interaction.user.id, motivo, observacao, tipo_novo, validade))
    conn.commit()

    if tipo_novo == "Adv3":
        cargo_ban = interaction.guild.get_role(Ban)
        if cargo_ban:
            await usuario.add_roles(cargo_ban)
            ban_msg = f"\n⚠️ {usuario.mention} Foi **Banido** por atingir o limite de advertências."
        else:
            ban_msg = "\n⚠️ Cargo de Ban não encontrado!"
    else:
        ban_msg = ""

    cursor.close()
    conn.close()

    canal_advs = interaction.guild.get_channel(Advertencias)
    if canal_advs:
        embed = discord.Embed(
            title="📢 Nova advertência:",
            color=discord.Color.orange()
        )
        embed.add_field(name="👤 Usuário:", value=f"<@{usuario.id}>", inline=True)
        embed.add_field(name="👮 Advertido por:", value=f"<@{interaction.user.id}>", inline=True)
        embed.add_field(name="⚠️ Advertência:", value=f"{tipo_novo} ({len(tipos_ativos)+1}/4)", inline=False)
        embed.add_field(name="📝 Motivo:", value=motivo, inline=False)
        embed.add_field(name="🕓 Data:", value=f"{hoje.strftime('%d/%m/%Y, %H:%M:%S')}", inline=False)
        embed.set_thumbnail(url=usuario.avatar.url if usuario.avatar else discord.Embed.Empty)
        embed.set_footer(text="Midnight RP © Todos os direitos reservados.")
        await canal_advs.send(embed=embed)

    await interaction.response.send_message(
        f"✅ {usuario.mention} recebeu a advertência do tipo **{tipo_novo}**.\nMotivo: {motivo}\nObservação: {observacao or 'Nenhuma'}{ban_msg}"
    )

#############################
# -= Mostrar Advertência =- #
#############################

@bot.tree.command(name="advs", description="Ver advertências ativas de um usuário", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(usuario="Usuário para verificar as advertências")
async def advs_command(interaction: discord.Interaction, usuario: discord.Member):
    permitted_roles = [Admin, Mod, Suporte, Auxiliar, Equipe]
    if not any(role.id in permitted_roles for role in interaction.user.roles):
        await interaction.response.send_message("⛔ Você não tem permissão para usar este comando.", ephemeral=True)
        return

    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM advertencias
        WHERE user_id = %s AND removida = FALSE
        ORDER BY data DESC
    """, (usuario.id,))
    advertencias_ativas = cursor.fetchall()
    cursor.close()
    conn.close()

    if not advertencias_ativas:
        await interaction.response.send_message(f"{usuario.mention} não possui advertências ativas.", ephemeral=True)
        return

    embed = discord.Embed(title=f"Advertências Ativas de {usuario.display_name}", color=discord.Color.orange())
    for adv in advertencias_ativas:
        data_str = adv['data'].strftime("%d/%m/%Y %H:%M")
        obs = adv['observacao'] if adv['observacao'] else "Nenhuma"
        embed.add_field(
            name=f"Tipo: {adv['tipo']} - Data: {data_str}",
            value=f"Motivo: {adv['motivo']}\nObservação: {obs}",
            inline=False
        )
    await interaction.response.send_message(embed=embed)

#############################
# -= Remover Advertência =- #
#############################

@bot.tree.command(name="remover_adv", description="Remover uma advertência ativa", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(adv_id="ID da advertência", motivo="Motivo da remoção")
async def remover_adv_command(interaction: discord.Interaction, adv_id: int, motivo: str):
    permitted_roles = [Owner, Admin, Mod]
    if not any(role.id in permitted_roles for role in interaction.user.roles):
        await interaction.response.send_message("⛔ Você não tem permissão para usar este comando.", ephemeral=True)
        return

    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM advertencias WHERE id = %s AND removida = FALSE", (adv_id,))
    adv = cursor.fetchone()

    if not adv:
        await interaction.response.send_message("❌ Advertência não encontrada ou já removida.", ephemeral=True)
        return

    cursor.execute("UPDATE advertencias SET removida = TRUE WHERE id = %s", (adv_id,))
    conn.commit()
    cursor.close()
    conn.close()

    canal_remocao = interaction.guild.get_channel(Remocao)
    if canal_remocao:
        embed = discord.Embed(
            title="❌ Advertência Removida",
            color=discord.Color.red()
        )
        embed.add_field(name="👤 Usuário", value=f"<@{adv['user_id']}>", inline=True)
        embed.add_field(name="👮 Removida por", value=f"<@{interaction.user.id}>", inline=True)
        embed.add_field(name="📌 Motivo original", value=adv['motivo'], inline=False)
        embed.add_field(name="📤 Motivo da remoção", value=motivo, inline=False)
        embed.add_field(name="📆 Data da Advertência", value=adv['data'].strftime("%d/%m/%Y, %H:%M:%S"), inline=False)
        embed.set_footer(text="Remoção registrada")
        await canal_remocao.send(embed=embed)

    await interaction.response.send_message("✅ Advertência removida com sucesso.", ephemeral=True)

#################
# -= SORTEIO =- #
#################

@bot.tree.command(name="sorteio", description="Inicia um sorteio com botão de participação", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(premio="Prêmio a ser sorteado")
async def sorteio_command(interaction: discord.Interaction, premio: str):
    canal_publico = interaction.guild.get_channel(Sorteio)
    if not canal_publico:
        await interaction.response.send_message("❌ Canal 'Sorteio' não encontrado.", ephemeral=True)
        return

    cargo_equipe = interaction.guild.get_role(Equipe)
    if not cargo_equipe:
        await interaction.response.send_message("❌ Cargo 'Equipe' não encontrado.", ephemeral=True)
        return

    categoria = discord.utils.get(interaction.guild.categories, id=SorteioC)
    if not categoria:
        await interaction.response.send_message("❌ Categoria 'SorteioC' não encontrada.", ephemeral=True)
        return

    overwrites = {
        interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
        cargo_equipe: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
    }

    canal_staff = await interaction.guild.create_text_channel(
        name=f"sorteio-{interaction.user.name}".lower(),
        overwrites=overwrites,
        category=categoria,
        topic=f"Monitoramento do sorteio de '{premio}'"
    )

    participantes = set()

    class StaffSorteioView(View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="🎯 Finalizar Sorteio", style=discord.ButtonStyle.red, custom_id="btn_finalizar_sorteio")
        async def finalizar(self, interaction_btn: discord.Interaction, button: Button):
            if interaction_btn.user.id != interaction.user.id:
                await interaction_btn.response.send_message("⛔ Apenas o organizador do sorteio pode finalizá-lo.", ephemeral=True)
                return

            if not participantes:
                await interaction_btn.response.send_message("❌ Ninguém participou do sorteio.", ephemeral=True)
                return

            vencedor_id = random.choice(list(participantes))
            vencedor = await interaction.guild.fetch_member(vencedor_id)

            await canal_publico.send(f"🎉 Parabéns {vencedor.mention}! Você ganhou o Sorteio de **{premio}**!")
            await interaction_btn.response.send_message(f"✅ Sorteio finalizado. Vencedor: {vencedor.display_name}", ephemeral=True)
            await canal_staff.send(f"🏆 Vencedor sorteado: {vencedor.mention}")

    class PublicoSorteioView(View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="📝 Participar do Sorteio", style=discord.ButtonStyle.green, custom_id="btn_participar_sorteio")
        async def participar(self, interaction_btn: discord.Interaction, button: Button):
            user_id = interaction_btn.user.id
            if user_id in participantes:
                await interaction_btn.response.send_message("⚠️ Você já está participando!", ephemeral=True)
                return

            participantes.add(user_id)
            await interaction_btn.response.send_message("✅ Você está participando do sorteio!", ephemeral=True)
            await canal_staff.send(f"📌 {interaction_btn.user.mention} entrou no sorteio de **{premio}**.")

    embed_publico = discord.Embed(
        title="🎉 Sorteio Iniciado!",
        description=f"📦 Prêmio: **{premio}**\nClique no botão abaixo para participar!",
        color=discord.Color.gold()
    )
    embed_publico.set_footer(text=f"Iniciado por {interaction.user.display_name}")
    await canal_publico.send(embed=embed_publico, view=PublicoSorteioView())

    embed_staff = discord.Embed(
        title="🎁 Painel do Sorteio",
        description="Aqui serão listados os participantes à medida que entrarem.\n\nUse o botão abaixo para sortear o vencedor quando quiser.",
        color=discord.Color.red()
    )
    embed_staff.add_field(name="Prêmio", value=premio, inline=False)
    embed_staff.set_footer(text="Midnight RP © Todos os direitos reservados.")
    await canal_staff.send(embed=embed_staff, view=StaffSorteioView())

    await interaction.response.send_message(f"✅ Sorteio criado com sucesso! Monitoramento: {canal_staff.mention}", ephemeral=True)

######################
# -= Atualizações =- #
######################

@bot.tree.command(name="att", description="Cria uma mensagem informando uma atualização", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    numero="Número da atualização",
    nome="Nome da atualização",
    descricao="Descrição da atualização",
    extras="Informações extras (opcional)"
)
async def att_command(interaction: discord.Interaction, numero: str, nome: str, descricao: str, extras: str = None):
    if interaction.user.id != Leonne:
        await interaction.response.send_message("❌ Você não tem permissão para usar este comando.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title=f"📢 Atualização #{numero}: {nome}",
        description=descricao,
        color=discord.Color.green()
    )
    if extras:
        embed.add_field(name="Extras", value=extras, inline=False)
    canal = interaction.guild.get_channel(Att)
    if canal:
        await canal.send(embed=embed)
    else:
        await interaction.response.send_message("❌ O canal de divulgação não foi encontrado.", ephemeral=True)

#############################
# -= Postagens da Equipe =- #
#############################

@bot.tree.command(name="div", description="Divulgação de membro da equipe", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    membro="Membro a ser divulgado",
    cargo="Cargo do membro na staff",
    post="Número do post (ex: 3/4)",
    instagram="Link do Instagram (opcional)",
    tiktok="Link do TikTok (opcional)",
    youtube="Link do YouTube (opcional)"
)
async def div_command(
    interaction: discord.Interaction,
    membro: discord.Member,
    cargo: discord.Role,
    post: str,
    instagram: str = None,
    tiktok: str = None,
    youtube: str = None
):
    # Verifica se o autor é o ID autorizado
    roles_ids = [role.id for role in interaction.user.roles]

    if Equipe not in roles_ids:
        await interaction.response.send_message("❌ Você não tem permissão para usar este comando.", ephemeral=True)
        return

    embed = discord.Embed(
        title=f"📣 Divulgação de Equipe — {post}",
        color=discord.Color.purple()
    )
    embed.add_field(name="👤 Membro", value=membro.mention, inline=True)
    embed.add_field(name="🎖 Cargo", value=cargo.mention, inline=True)

    if instagram:
        embed.add_field(name="📸 Instagram", value=instagram, inline=False)
    if tiktok:
        embed.add_field(name="🎵 TikTok", value=tiktok, inline=False)
    if youtube:
        embed.add_field(name="▶️ YouTube", value=youtube, inline=False)

    canal = interaction.guild.get_channel(Postar)
    if canal:
        await canal.send(embed=embed)
        await interaction.response.send_message(f"✅ Divulgação enviada com sucesso em {canal.mention}.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ O canal de divulgação não foi encontrado.", ephemeral=True)

########################
# -= Feedback Calls =- #
########################

@bot.tree.command(name="feedback", description="Enviar feedback para membro da staff", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    membro="Membro da staff que lhe atendeu",
    nota="Nota (ex: '7', '8.5', '10')",
    descricao="Comentário opcional"
)
async def feedback_command(interaction: discord.Interaction, membro: discord.Member, nota: str, descricao: str = None):
    try:
        nota_float = float(nota.replace(',', '.'))  # Aceita vírgula ou ponto
    except ValueError:
        await interaction.response.send_message("❌ Nota inválida! Use um número entre 0 e 10.", ephemeral=True)
        return

    if nota_float < 0 or nota_float > 10:
        await interaction.response.send_message("❌ A nota deve estar entre 0 e 10.", ephemeral=True)
        return

    await interaction.response.send_message("✅ Feedback enviado com sucesso!", ephemeral=True)

    embed = discord.Embed(
        title="📝 Novo Feedback Recebido",
        color=discord.Color.green(),
        timestamp=datetime.datetime.utcnow()
    )
    embed.add_field(name="👤 Staff Avaliado", value=membro.mention, inline=True)
    embed.add_field(name="⭐ Nota", value=nota, inline=True)
    embed.add_field(name="📋 Comentário", value=descricao or "Nenhum", inline=False)
    embed.add_field(name="🙍 Enviado por", value=interaction.user.mention, inline=True)

    canal = interaction.guild.get_channel(FeedC)
    if canal:
        await canal.send(embed=embed)
    else:
        await interaction.followup.send("❌ Canal de feedback não encontrado.", ephemeral=True)

#################
# -= Tickets =- #
#################

# Classe de controle com botões dentro do canal do ticket
class TicketControlView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Fechar", style=ButtonStyle.secondary, custom_id="fechar_ticket")
    async def fechar(self, interaction: discord.Interaction, button: discord.ui.Button):
        staff_role = interaction.guild.get_role(1354778352489336942)
        if staff_role not in interaction.user.roles:
            await interaction.response.send_message("⛔ Apenas membros da equipe Staff podem fechar tickets.", ephemeral=True)
            return
        await interaction.channel.edit(name=f"fechado-{interaction.channel.name}")
        await interaction.response.send_message("🔒 Ticket fechado com sucesso.", ephemeral=True)

    @discord.ui.button(label="➕ Adicionar membro", style=ButtonStyle.primary, custom_id="add_member")
    async def adicionar(self, interaction: discord.Interaction, button: discord.ui.Button):
        staff_role = interaction.guild.get_role(1354778352489336942)
        if staff_role not in interaction.user.roles:
            await interaction.response.send_message("⛔ Apenas membros da equipe Staff podem adicionar membros.", ephemeral=True)
            return
        def check(m):
            return m.channel == interaction.channel and m.author == interaction.user

        await interaction.response.send_message("✍️ Envie uma mensagem mencionando o membro que deseja adicionar.", ephemeral=True)
        try:
            msg = await bot.wait_for("message", timeout=30.0, check=check)
            if msg.mentions:
                membro = msg.mentions[0]
                await interaction.channel.set_permissions(membro, read_messages=True, send_messages=True)
                await interaction.followup.send(f"✅ {membro.mention} foi adicionado ao ticket.", ephemeral=False)
            else:
                await interaction.followup.send("❌ Nenhum membro mencionado.", ephemeral=True)
        except asyncio.TimeoutError:
            await interaction.followup.send("⏰ Tempo esgotado. Nenhum membro foi adicionado.", ephemeral=True)

    @discord.ui.button(label="➖ Remover membro", style=ButtonStyle.danger, custom_id="remove_member")
    async def remover(self, interaction: discord.Interaction, button: discord.ui.Button):
        staff_role = interaction.guild.get_role(1354778352489336942)
        if staff_role not in interaction.user.roles:
            await interaction.response.send_message("⛔ Apenas membros da equipe Staff podem remover membros.", ephemeral=True)
            return
        def check(m):
            return m.channel == interaction.channel and m.author == interaction.user

        await interaction.response.send_message("✍️ Envie uma mensagem mencionando o membro que deseja remover.", ephemeral=True)
        try:
            msg = await bot.wait_for("message", timeout=30.0, check=check)
            if msg.mentions:
                membro = msg.mentions[0]
                await interaction.channel.set_permissions(membro, overwrite=None)
                await interaction.followup.send(f"✅ {membro.mention} foi removido do ticket.", ephemeral=False)
            else:
                await interaction.followup.send("❌ Nenhum membro mencionado.", ephemeral=True)
        except asyncio.TimeoutError:
            await interaction.followup.send("⏰ Tempo esgotado. Nenhum membro foi removido.", ephemeral=True)

# Classe de seleção para tickets
class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Bug", description="Esclarecimento de Algum erro do Sistema", emoji="🐛"),
            discord.SelectOption(label="Denúncia", description="Relatar jogadores", emoji="🚨"),
            discord.SelectOption(label="Doação", description="Esclarecimento de Doações e ajudas afins", emoji="💰"),
            discord.SelectOption(label="Dúvida", description="Esclarecimento de dúvidas", emoji="❓"),
            discord.SelectOption(label="Suporte", description="Atendimento Geral", emoji="🛠️")
        ]
        super().__init__(placeholder="Escolha a categoria do seu ticket", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        categoria = self.values[0]
        emojis = {
            "Suporte": "🛠️",
            "Denúncia": "🚨",
            "Dúvida": "❓",
            "Bug": "🐛",
            "Doação": "💰"
            }
        emoji = emojis.get(categoria, "🎟️")

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS ticket_counter (id INT PRIMARY KEY AUTO_INCREMENT, dummy INT)")
            cursor.execute("INSERT INTO ticket_counter (dummy) VALUES (1)")
            conn.commit()
            cursor.execute("SELECT COUNT(*) FROM ticket_counter")
            ticket_number = cursor.fetchone()[0]
            cursor.close()
            conn.close()
        except Exception as e:
            await interaction.response.send_message(f"❌ Erro ao acessar banco: {e}", ephemeral=True)
            return

        nome_canal = f"ticket-{ticket_number:05d}-{emoji}"

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True),
        }

        canal = await interaction.guild.create_text_channel(
            name=nome_canal,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title=f"{emoji} {categoria}",
            description="Explique sua situação para que a equipe possa ajudar.",
            color=discord.Color.blurple()
        )
        embed.set_footer(text=f"Ticket criado por {interaction.user.display_name} • {datetime.datetime.now():%d/%m/%Y %H:%M}")

        view = TicketControlView()
        await canal.send(content=interaction.user.mention, embed=embed, view=view)
        await interaction.response.send_message(f"✅ Ticket criado: {canal.mention}", ephemeral=True)

class FeedbackModal(Modal, title="Feedback do Ticket"):
    nota = TextInput(label="Nota para o atendimento (0-10)", placeholder="Ex: 8.5", required=True, max_length=4)
    comentario = TextInput(label="Comentário (opcional)", style=discord.TextStyle.paragraph, required=False)

    def __init__(self, usuario, canal_ticket):
        super().__init__()
        self.usuario = usuario
        self.canal_ticket = canal_ticket

    async def on_submit(self, interaction: discord.Interaction):


        nota_texto = self.nota.value
        comentario_texto = self.comentario.value or "Nenhum comentário"

        try:
            nota_float = float(nota_texto.replace(',', '.'))
            if nota_float < 0 or nota_float > 10:
                raise ValueError
        except:
            await interaction.response.send_message("❌ Nota inválida! Use um número entre 0 e 10.", ephemeral=True)
            return

        embed = discord.Embed(
            title="📝 Feedback de Ticket Recebido",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="👤 Usuário", value=self.usuario.mention, inline=True)
        embed.add_field(name="⭐ Nota", value=nota_texto, inline=True)
        embed.add_field(name="📋 Comentário", value=comentario_texto, inline=False)
        embed.add_field(name="📁 Canal do Ticket", value=self.canal_ticket.mention, inline=True)
        embed.add_field(name="🙍 Enviado por", value=interaction.user.mention, inline=True)

        canal = interaction.guild.get_channel(FeedT)
        if canal:
            await canal.send(embed=embed)
            await interaction.response.send_message("✅ Feedback enviado com sucesso!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Canal de feedback não encontrado.", ephemeral=True)

@bot.tree.command(name="ticket", description="Abre o menu fixo para abrir um ticket", guild=discord.Object(id=GUILD_ID))
async def ticket_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎟️ Central de Tickets",
        description="Use o menu abaixo para abrir um ticket com a equipe. Um canal exclusivo será criado para seu atendimento.",
        color=discord.Color.gold()
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/1354778353290187029/1356994548907380806/Imagem_do_WhatsApp_de_2025-03-27_as_11.20.49_457e51be.jpg")
    embed.set_footer(text="Midnight RP © Todos os direitos reservados.")
    await interaction.response.send_message(embed=embed, view=TicketView(), ephemeral=False)

async def ticket_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎟️ Central de Tickets",
        description="Use o menu abaixo para abrir um ticket com a equipe. Um canal exclusivo será criado para seu atendimento.",
        color=discord.Color.gold()
    )
    await interaction.response.send_message(embed=embed, view=TicketView())
async def ticket_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎟️ Ticket de Suporte",
        description="Selecione uma opção de acordo com o assunto que deseja tratar com um staff.",
        color=discord.Color.blue()
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/1354778353290187029/1356994548907380806/Imagem_do_WhatsApp_de_2025-03-27_as_11.20.49_457e51be.jpg")
    embed.add_field(
        name="📌 Observações:",
        value="🔹 Cada tipo de ticket é exclusivo para tratar sobre o assunto selecionado.\n🔹 Não abra um ticket sem um bom motivo. Poderá resultar em punição.",
        inline=False
    )
    embed.set_footer(text="Midnight RP © Todos os direitos reservados.")
    await interaction.response.send_message(embed=embed, view=TicketView(), ephemeral=True)

################
# -= Staffs =- #
################

cargos_dict = {
    "Owner": Owner,
    "Admin": Admin,
    "Mod": Mod,
    "Suporte": Suporte,
    "Auxiliar": Auxiliar
}

@bot.tree.command(name="staff", description="Lista os membros da equipe online com cargos e tempo ativo", guild=discord.Object(id=GUILD_ID))
@app_commands.describe()
async def staff(interaction: discord.Interaction):
    guild = interaction.guild
    
    embed = discord.Embed(
        title="👥 Equipe Online",
        color=discord.Color.blue(),
        timestamp=datetime.now(tz=timezone.utc)
    )

    for nome_cargo, cargo_id in cargos_dict.items():
        cargo = guild.get_role(cargo_id)
        if not cargo:
            continue

        membros_ativos = []
        for membro in guild.members:
            if cargo in membro.roles and membro.status != discord.Status.offline:
                tempo_online_str = str(membro.status).capitalize()
                membros_ativos.append(f"{membro.mention} - **Status:** {tempo_online_str}")

        if membros_ativos:
            embed.add_field(name=f"🔹 {nome_cargo}s Online", value="\n".join(membros_ativos), inline=False)
        else:
            embed.add_field(name=f"🔹 {nome_cargo}s Online", value="Nenhum membro online.", inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

##############
# -= Ponto =-#
##############

pontos_em_andamento = {}

# Classe com os botões de ponto
class PontoView(View):
    def __init__(self, interaction: Interaction, registro_id: int, inicio: datetime):
        super().__init__(timeout=None)
        self.user_id = interaction.user.id
        self.registro_id = registro_id
        self.inicio = inicio
        self.pause_time = None
        self.total_paused = timedelta()
        self.embed = Embed(title="📍 Registro de Ponto", color=discord.Color.green())
        self.embed.add_field(name="👤 Usuário", value=interaction.user.mention, inline=True)
        self.embed.add_field(name="🕓 Início", value=inicio.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
        self.message = None

    @button(label="⏸️ Pausar", style=ButtonStyle.danger)
    async def pausar(self, interaction: Interaction, button: Button):
        if self.pause_time:
            await interaction.response.send_message("⚠️ Já está pausado.", ephemeral=True)
            return

        self.pause_time = datetime.now()

        # Atualiza no banco
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE pontos SET pausado = %s WHERE id = %s", (self.pause_time, self.registro_id))
        conn.commit()
        cursor.close()
        conn.close()

        self.embed.add_field(name="⏸️ Pausado em", value=self.pause_time.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
        await self.message.edit(embed=self.embed, view=self)
        await interaction.response.send_message("⏸️ Ponto pausado.", ephemeral=True)

    @button(label="▶️ Retomar", style=ButtonStyle.success)
    async def retomar(self, interaction: Interaction, button: Button):
        if not self.pause_time:
            await interaction.response.send_message("⚠️ Nenhuma pausa ativa para retomar.", ephemeral=True)
            return

        retomado = datetime.now()
        tempo_paused = retomado - self.pause_time
        self.total_paused += tempo_paused

        # Atualiza no banco
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE pontos SET retomado = %s WHERE id = %s", (retomado, self.registro_id))
        conn.commit()
        cursor.close()
        conn.close()

        self.embed.add_field(name="▶️ Retomado em", value=retomado.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
        self.pause_time = None
        await self.message.edit(embed=self.embed, view=self)
        await interaction.response.send_message("▶️ Retomado com sucesso.", ephemeral=True)

    @button(label="✅ Finalizar", style=ButtonStyle.primary)
    async def finalizar(self, interaction: Interaction, button: Button):
        if self.user_id != interaction.user.id:
            await interaction.response.send_message("⛔ Apenas quem iniciou pode finalizar.", ephemeral=True)
            return

        fim = datetime.now()
        total = fim - self.inicio - self.total_paused

        # Salva no banco
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE pontos
            SET fim = %s, total_segundos = %s
            WHERE id = %s
        """, (fim, int(total.total_seconds()), self.registro_id))
        conn.commit()
        cursor.close()
        conn.close()

        self.embed.add_field(name="✅ Finalizado em", value=fim.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
        self.embed.add_field(name="⏳ Duração total", value=str(total).split('.')[0], inline=False)
        self.embed.color = discord.Color.greyple()
        self.clear_items()
        await self.message.edit(embed=self.embed, view=self)
        await interaction.response.send_message("✅ Ponto finalizado com sucesso.", ephemeral=True)

        pontos_em_andamento.pop(self.user_id, None)

# Comando principal
@bot.tree.command(name="ponto", description="Inicia um ponto com controle de pausa, retomada e finalização.", guild=discord.Object(id=GUILD_ID))
async def ponto_command(interaction: Interaction):
    user_id = interaction.user.id
    if user_id in pontos_em_andamento:
        await interaction.response.send_message("⚠️ Você já tem um ponto em andamento.", ephemeral=True)
        return

    inicio = datetime.now()

    # Insere no banco
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pontos (user_id, inicio) VALUES (%s, %s)", (user_id, inicio))
    registro_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()

    view = PontoView(interaction, registro_id, inicio)
    msg = await interaction.channel.send(embed=view.embed, view=view)
    view.message = msg
    pontos_em_andamento[user_id] = view

    await interaction.response.send_message("🕓 Ponto iniciado com sucesso!", ephemeral=True)

bot.run(TOKEN)
