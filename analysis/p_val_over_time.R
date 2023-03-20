pacman::p_load(tidyverse, plotly)
#path = "C:\\Python\\Titta-master\\demos\\logs\\finals\\no-color-change-min30-zscore\\stat\\no color change & not first & no update & correct vs no color change & not first & update & correct.csv"
path = "C:\\Python\\Titta-master\\demos\\logs\\finals\\24.5-min30\\stat\\no color change & not first & no update & correct vs no color change & not first & update & correct.csv"
#path = "C:\\Python\\Titta-master\\demos\\logs\\finals\\24.5-min30-percentage\\stat\\no color change & not first & no update & correct vs no color change & not first & update & correct.csv"
p_values = read.csv(path)
p_values = p_values[-1,]
p_values$pValues = p_values$pValues %>% round(3)
p_values$x_axis = p_values$x_axis %>% round
p_values$x_end = c(p_values$x_axis[-1], 0)
p_values$y_end = c(p_values$pValues[-1], 0)
p_values = p_values[- nrow(p_values),]
alpha = 0.05

p_values %>% filter(pValues < 0.05) %>% 
  filter(between(x_axis, 1900,2300)) %>%
  select(pValues, x_axis) %>% c

g = p_values %>%
  mutate(Result = if_else(pValues < alpha & y_end < alpha, 
                               'Significant', 'Not\nSignificant')) %>%
  #filter(between(x_axis, 1600,2300)) %>%
  ggplot +
  geom_segment(aes(x=x_axis,xend=x_end, y=pValues, yend=y_end, color = Result), size=1) +
  geom_point(aes(x = x_axis,y = pValues), size=1) +
  #geom_label(aes(x = x_axis,y = pValues + 0.01, label=round(pValues,3) %>% substring(2,5)), alpha=0.4) +
  scale_color_manual(values=c("brown3","#48cbd1")) +
  labs(title='p-value over time',
       subtitle='distance between data points is approx 25ms',
       x='miliseconds') +
  scale_x_continuous(breaks = seq(20,3000,100)) +
  scale_y_continuous(breaks = seq(0,1,0.05)) +
  geom_hline(yintercept = alpha, linetype='dot', color='black', size=0.3)
  # geom_text(x=1100, y=0.07, label='p-val')

ggplotly(g)

