# -------------------- Charger les bibliothèques nécessaires --------------------
library(xts)        # Pour la gestion des séries temporelles
library(ggplot2)    # Pour la visualisation des données
library(quantmod)   # Pour télécharger les données boursières
library(prophet)    # Pour la modélisation des séries temporelles
library(dplyr)      # Pour la manipulation des données

# -------------------- Charger les données de l'action ADBE (Adobe) depuis Yahoo Finance --------------------
getSymbols("ADBE", from = "2010-01-01", to = "2024-10-31", src = "yahoo")

# -------------------- Extraire les prix ajustés d'Adobe --------------------
adobe_prices <- ADBE$ADBE.Adjusted

# -------------------- Enlever la première observation du prix pour que cela corresponde aux données de volatilité --------------------
adobe_prices <- adobe_prices[-1]

# -------------------- Calcul des rendements log-transformés des prix d'Adobe --------------------
#adobe_returns <- na.omit(diff(log(adobe_prices)))

# -------------------- Préparer les données pour l'analyse --------------------
adobe_data <- data.frame(
  ds = index(adobe_prices),           # Date des observations
  y = as.numeric(adobe_prices)        # Prix de l'action
)

# Ajouter les colonnes de date (mois, jour, année)
adobe_data$month <- format(adobe_data$ds, "%m")
adobe_data$year <- format(adobe_data$ds, "%Y")
adobe_data$day <- format(adobe_data$ds, "%d")

# Extraire le jour de la semaine
adobe_data$day_of_week <- weekdays(adobe_data$ds)

# Vérifier un aperçu des données
head(adobe_data)

# -------------------- Visualisation de la volatilité --------------------
plot(y = adobe_data$y, x = adobe_data$ds, main = "", 
     ylab = "Prix", col = "blue", type = "l", xlab = "")

# -------------------- Tracer par mois --------------------
# Boxplot de la distribution des rendements par mois
ggplot(adobe_data, aes(x = month, y = y)) +
  geom_boxplot() +
  labs(
    title = "Distribution mensuelle des rendements",
    x = "Mois",
    y = "Rendement"
  ) +
  theme_minimal()

# Densité des rendements par mois
ggplot(adobe_data, aes(x = y, fill = month)) +
  geom_density(alpha = 0.5) +
  labs(
    title = "Densité des rendements par mois",
    x = "Rendement",
    y = "Densité"
  ) +
  theme_minimal()

# -------------------- Tracer par jour du mois --------------------
# Boxplot de la distribution des rendements par jour
ggplot(adobe_data, aes(x = day, y = y)) +
  geom_boxplot() +
  labs(
    title = "Distribution journalière des rendements",
    x = "Jour",
    y = "Rendement"
  ) +
  theme_minimal()

# Densité des rendements par jour
ggplot(adobe_data, aes(x = y, fill = day)) +
  geom_density(alpha = 0.5) +
  labs(
    title = "Densité des rendements par jour du mois",
    x = "Rendement",
    y = "Densité"
  ) +
  theme_minimal()

# -------------------- Tracer par jour de la semaine --------------------
# Boxplot de la distribution des rendements par jour de la semaine
ggplot(adobe_data, aes(x = day_of_week, y = y)) +
  geom_boxplot() +
  labs(
    title = "Distribution hebdomadaire",
    x = "Jour de la semaine",
    y = "Volatilité"
  ) +
  theme_minimal()

# Densité des rendements par jour de la semaine
ggplot(adobe_data, aes(x = y, fill = day_of_week)) +
  geom_density(alpha = 0.5) +
  labs(
    title = "Densité par jour de la semaine",
    x = "Volatilité",
    y = "Densité"
  ) +
  theme_minimal()

# -------------------- Importer les données de volatilité --------------------
# Importer les données CSV avec les colonnes Volatility et SquaredVolatility
data <- read.csv("E:/ENSAI/ENSAI 3A/Series temp avancées/Projet_serie_temp/Stock-Price-Prediction/volatilite_estimee.csv")

# Afficher les premières lignes du fichier pour vérifier le format
head(data)

# Convertir la colonne de date en format Date
data$Date <- as.Date(data$Date)

# Extraire les colonnes Volatility et SquaredVolatility
regressor_data <- data[, c("Date", "Volatility", "SquaredVolatility")]

# Renommer les colonnes pour correspondre à l'input du modèle Prophet
colnames(regressor_data) <- c("ds", "volatility", "squared_volatility")
head(regressor_data)
nrow(regressor_data)
nrow(adobe_data)

# -------------------- Fusionner les données de volatilité et de rendements Adobe --------------------
adobe_data$volatility <- regressor_data$volatility
adobe_data$squared_volatility <- regressor_data$squared_volatility

head(adobe_data)

# -------------------- Diviser les données en ensemble d'entraînement et de test --------------------
train_end_date <- as.Date("2024-08-30")  # Date de fin de l'ensemble d'entraînement
train_data <- adobe_data[adobe_data$ds <= train_end_date, ]
test_data <- adobe_data[adobe_data$ds > train_end_date, ]

# Créer les colonnes de régressors pour les événements macroéconomiques dans train_data
train_data$sovereign_debt_crisis <- as.integer(train_data$ds >= as.Date("2010-01-01") & train_data$ds <= as.Date("2012-12-31"))
train_data$oil_shock <- as.integer(train_data$ds >= as.Date("2014-01-01") & train_data$ds <= as.Date("2016-12-31"))
train_data$trade_war <- as.integer(train_data$ds >= as.Date("2018-01-01") & train_data$ds <= as.Date("2019-12-31"))
train_data$covid_pandemic <- as.integer(train_data$ds >= as.Date("2020-01-01") & train_data$ds <= as.Date("2022-12-31"))
train_data$war_ukraine <- as.integer(train_data$ds >= as.Date("2022-02-24"))

# -------------------- Créer un dataframe pour Prophet avec les régressors --------------------
prophet_train_data <- data.frame(
  ds = as.Date(train_data$ds),
  y = train_data$y
)

# Ajouter les régressors à Prophet
prophet_train_data$volatility <- train_data$volatility
prophet_train_data$squared_volatility <- train_data$squared_volatility
prophet_train_data$sovereign_debt_crisis <- train_data$sovereign_debt_crisis
prophet_train_data$oil_shock <- train_data$oil_shock
prophet_train_data$trade_war <- train_data$trade_war
prophet_train_data$covid_pandemic <- train_data$covid_pandemic
prophet_train_data$war_ukraine <- train_data$war_ukraine

head(prophet_train_data)

# -------------------- Créer et ajuster le modèle Prophet --------------------
model <- prophet(
  yearly.seasonality = TRUE,
  weekly.seasonality = TRUE,
  daily.seasonality = FALSE
)

# Ajouter les régressors de volatilité et des événements macroéconomiques
model <- add_regressor(model, 'volatility')
model <- add_regressor(model, 'squared_volatility')
model <- add_regressor(model, 'sovereign_debt_crisis')
model <- add_regressor(model, 'oil_shock')
model <- add_regressor(model, 'trade_war')
model <- add_regressor(model, 'covid_pandemic')
model <- add_regressor(model, 'war_ukraine')

# Ajuster le modèle aux données d'entraînement
fit <- fit.prophet(model, prophet_train_data)

# -------------------- Créer la dataframe future pour la prévision --------------------
future <- make_future_dataframe(fit, periods = nrow(test_data))
future$ds <- as.POSIXct(future$ds, tz = "UTC")

# Ajouter les régressors dans le futur
future <- future %>%
  mutate(
    sovereign_debt_crisis = as.integer(ds >= as.POSIXct("2010-01-01", tz = "UTC") & ds <= as.POSIXct("2012-12-31", tz = "UTC")),
    oil_shock = as.integer(ds >= as.POSIXct("2014-01-01", tz = "UTC") & ds <= as.POSIXct("2016-12-31", tz = "UTC")),
    trade_war = as.integer(ds >= as.POSIXct("2018-01-01", tz = "UTC") & ds <= as.POSIXct("2019-12-31", tz = "UTC")),
    covid_pandemic = as.integer(ds >= as.POSIXct("2020-01-01", tz = "UTC") & ds <= as.POSIXct("2022-12-31", tz = "UTC")),
    war_ukraine = as.integer(ds >= as.POSIXct("2022-02-24", tz = "UTC")),
    volatility = adobe_data$volatility,
    squared_volatility = adobe_data$squared_volatility
  )

# -------------------- Visualisation des prévisions --------------------
forecast <- predict(fit, future)

# S'assurer que la première date de forecast correspond à la première date de test_data
forecast$ds <- adobe_data$ds

# Tracer les prévisions
plot(fit, forecast)

# Visualisation des prévisions et des composantes
prophet_plot_components(fit, forecast)

# Visualisation de la prévision avec les intervalles d'incertitude
dyplot.prophet(fit, forecast)

# -------------------- Comparaison des données réelles et des prédictions du test --------------------
test_data$ds <- as.Date(test_data$ds)
forecast$ds <- as.Date(forecast$ds)

# Tracer les données réelles et les prédictions
ggplot() +
  geom_line(data = test_data, aes(x = ds, y = y), color = "blue", linewidth = 1, alpha = 0.7, linetype = "dashed") +
  geom_line(data = forecast, aes(x = ds, y = yhat), color = "red", linewidth = 1) +
  geom_ribbon(data = forecast, aes(x = ds, ymin = yhat_lower, ymax = yhat_upper), fill = "red", alpha = 0.2) +
  labs(title = "Prédictions de prix d'Adobe vs. Réalités du test",
       x = "Date",
       y = "Prix") +
  theme_minimal() +
  theme(legend.position = "none")




#--------------------------------------------- Juste pour test
future <- make_future_dataframe(fit, periods = nrow(test_data), include_history = FALSE)
future$ds <- as.POSIXct(future$ds, tz = "UTC")

# Ajouter les régressors dans le futur
future <- future %>%
  mutate(
    sovereign_debt_crisis = as.integer(ds >= as.POSIXct("2010-01-01", tz = "UTC") & ds <= as.POSIXct("2012-12-31", tz = "UTC")),
    oil_shock = as.integer(ds >= as.POSIXct("2014-01-01", tz = "UTC") & ds <= as.POSIXct("2016-12-31", tz = "UTC")),
    trade_war = as.integer(ds >= as.POSIXct("2018-01-01", tz = "UTC") & ds <= as.POSIXct("2019-12-31", tz = "UTC")),
    covid_pandemic = as.integer(ds >= as.POSIXct("2020-01-01", tz = "UTC") & ds <= as.POSIXct("2022-12-31", tz = "UTC")),
    war_ukraine = as.integer(ds >= as.POSIXct("2022-02-24", tz = "UTC")),
    volatility = test_data$volatility,
    squared_volatility = test_data$squared_volatility
  )

# -------------------- Visualisation des prévisions --------------------
forecast <- predict(fit, future)

# S'assurer que la première date de forecast correspond à la première date de test_data
forecast$ds <- test_data$ds


# Tracer les données réelles et les prédictions
ggplot() +
  geom_line(data = test_data, aes(x = ds, y = y), color = "blue", linewidth = 1, alpha = 0.7, linetype = "dashed") +
  geom_line(data = forecast, aes(x = ds, y = yhat), color = "red", linewidth = 1) +
  geom_ribbon(data = forecast, aes(x = ds, ymin = yhat_lower, ymax = yhat_upper), fill = "red", alpha = 0.2) +
  labs(title = "Prédictions de prix d'Adobe vs. Réalités du test",
       x = "Date",
       y = "Prix") +
  theme_minimal() +
  theme(legend.position = "none")
