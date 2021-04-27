library(ggplot2)
library(doBy)
library(plyr)
library(scales)

dataSATDC <- read.csv(file="./datasets/selected/satdc_info_filtered.csv", 
                      header = TRUE, sep = ";")

png(file = "./plots/version2/out/png/c_age.png")

sizeSATDC <- dataSATDC$duration
#sizeSATDI <- dataSATDI$size + 1

values <- c(sizeSATDC)

vector = c()
cont = 0
for (i in 1:(length(values))) {
  if (i < length(dataSATDC$duration) + 1) {
    vector[i] <- "SATD-C"
  } 
}

dfchart <- data.frame(values, vector)
vector2 <- factor(dfchart$vector, c("SATD-C"))
dfchart$vector2 <- factor(dfchart$vector, c("SATD-C"))
aChart <- summaryBy(values ~ vector2, dfchart, FUN = c(median))
meds <- ddply(dfchart, .(vector2), summarize, med = median(values))

ggplot(dfchart, aes(vector2, values)) + 
  geom_violin(fill='grey') +
  geom_boxplot(outlier.shape = 5, alpha = 0.5) +
  ggtitle("Age") + 
  ylab("# days (log scale)") +
  geom_text(data = meds, aes(y = med, label = (round(med,2))),size = 8, vjust = -0.085,fontface = "bold") + 
  theme(axis.title.y = element_text(size=22, margin = margin(r = 10)), axis.text.y  = element_text(size=22), 
        axis.title.x = element_blank(), axis.text.x  = element_text(size=20),
        plot.title = element_text(size=24, face = "bold", margin = margin(b = 3), hjust = 0.5)) +
  scale_y_log10() 
dev.off()