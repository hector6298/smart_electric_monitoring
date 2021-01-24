void lcd_print(LiquidCrystal* lcd, float message, char* type){
  if (message < 10){
    lcd->print(type); lcd->print("  "); lcd->print(message);
  }
  else if (message < 100){
    lcd->print(type); lcd->print(" "); lcd->print(message);
  }
  else if(message < 1000){
    lcd->print(type); lcd->print(message);
  }
}
