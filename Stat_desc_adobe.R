library(quantmod)

# Get Adobe stock data (ADBE) from 2010-01-01 to 2024-10-31
adobe <- getSymbols("ADBE", env=NULL, from="2010-01-01", to="2024-10-31")

# Display the first few rows of the data
head(adobe)

# Extract the adjusted closing price
price_close <- adobe$ADBE.Adjusted

# Calculate logarithmic returns
returns <- diff(log(price_close)) * 100
length(returns)

# Remove missing values from the returns series
returns <- na.omit(returns)
length(returns)

# Calculate squared returns
returns_squared <- returns^2

# Display the first few rows of returns and squared returns
head(returns)
head(returns_squared)

# Compute mean and standard deviation of squared returns
mean(returns_squared)
sd(returns_squared)

# Center the squared returns by subtracting the mean
returns_squared_centered <- returns_squared - mean(returns_squared)

# Plot the adjusted closing price over time
plot(index(price_close), price_close, type="l", ylab="Closing Price", xlab="Time")

# Plot the returns over time
plot.ts(returns, ylab="Returns", xlab="Time")

# Autocorrelation plots of returns and squared returns
par(mfrow=c(1, 1))  # Reset plotting layout
acf(returns, ylab="Empirical Autocorrelation", main="", xlab="Lag")
pacf(returns, ylab="Empirical Autocorrelation", main="", xlab="Lag")


acf(returns_squared, ylab="Empirical Autocorrelation", main="", xlab="Lag")
pacf(returns_squared, ylab="Empirical Autocorrelation", main="", xlab="Lag")


# Calculate bandwidth for density estimation
hn <- 1.06 * sd(returns) * length(returns)^(-1/5)

# Plot the density estimation of returns
plot(density(returns, bw=hn, kernel="gaussian"), xlab="Returns", col="red", lwd=2, main="Density Estimation of Returns")

# Overlay a standard normal density curve for comparison
lines(density(rnorm(length(returns), mean=mean(returns), sd=sd(returns))), col="blue", lwd=2)

# Calculate the empirical mean and variance of returns
mean_empirical <- mean(returns)
variance_empirical <- var(returns)

# Calculate the optimal bandwidth for kernel density estimation
hn_optimal_ker <- 1.06 * sd(returns) * length(returns)^(-1/5)

# Plot the density estimator of the returns (solid line)
plot(density(returns), col="blue", main="", xlab="", xlim=c(-10, 10))

# Plot the normal density with the empirical mean and variance (dashed line)
curve(dnorm(x, mean=mean_empirical, sd=sqrt(variance_empirical)), add=TRUE, col="red", lty=2)

# Add a legend with a reduced box size
legend("topleft", legend=c("Density Estimator", "Normal Density"), col=c("blue", "red"), lty=c(1, 2), cex=0.8, bg="white", box.lwd=0.5, bty="n")
