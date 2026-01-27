//+------------------------------------------------------------------+
//|                                              ReadJsonParsed.mq5 |
//|                                  Lê e processa JSON estruturado  |
//+------------------------------------------------------------------+
#include <JAson.mqh> 

input string InpFileName = "main.json";   
input bool   InpUseCommon = true;        

void CreateObject(string objectName, double objectFirstLevelPoint, double objectSecondLevelPoint, datetime objectInitialPeriod, datetime objectFinalPeriod, color objectColor, int objectWidth)
{
   ObjectCreate(0, objectName, OBJ_TREND, 0, 0, 0);

   ObjectSetDouble(0, objectName, OBJPROP_PRICE, 0, objectFirstLevelPoint);
   ObjectSetDouble(0, objectName, OBJPROP_PRICE, 1, objectSecondLevelPoint);

   ObjectSetInteger(0, objectName, OBJPROP_TIME, 0, objectInitialPeriod);
   ObjectSetInteger(0, objectName, OBJPROP_TIME, 1, objectFinalPeriod);

   ObjectSetInteger(0, objectName, OBJPROP_COLOR, objectColor);
   ObjectSetInteger(0, objectName, OBJPROP_STYLE, STYLE_SOLID);
   ObjectSetInteger(0, objectName, OBJPROP_WIDTH, objectWidth);
   ObjectSetInteger(0, objectName, OBJPROP_RAY_RIGHT, false); // Estende para a direita
   ObjectSetInteger(0, objectName, OBJPROP_RAY_LEFT, false);  // Estende para a esquerda
   ObjectSetInteger(0, objectName, OBJPROP_BACK, false);     // Fica na frente
   ObjectSetInteger(0, objectName, OBJPROP_SELECTABLE, true); // Pode ser selecionada
   ObjectSetInteger(0, objectName, OBJPROP_SELECTED, false);  // Não inicia selecionada
   ObjectSetString(0, objectName, OBJPROP_TOOLTIP, objectName);
}

void AbrirArquivo(int flags)
{
   int fh = FileOpen(InpFileName, flags);
   if(fh == INVALID_HANDLE)
   {
      PrintFormat("Erro ao abrir '%s': %d", InpFileName, GetLastError());
   }
}

int OnInit(void)
{
   return(INIT_SUCCEEDED);
}

void OnTick()
{
   int flags = FILE_READ | FILE_BIN; 
   if(InpUseCommon) flags |= FILE_COMMON;
   
   int fh = FileOpen(InpFileName, flags);
   if(fh == INVALID_HANDLE)
   {
      PrintFormat("Erro ao abrir '%s': %d", InpFileName, GetLastError());
//      return(INVALID_HANDLE);
   }

   // 1. Ler o arquivo
   uint fileSize = (uint)FileSize(fh);
   uchar buffer[];
   ArrayResize(buffer, fileSize);
   FileReadArray(fh, buffer);
   string jsonContent = CharArrayToString(buffer);
   FileClose(fh);

   // 2. Parsear o JSON
   CJAVal json; 
   if(!json.Deserialize(jsonContent))
   {
      Print("Erro: JSON inválido ou mal formatado.");
//      return(INVALID_HANDLE);
   }

   // 3. Acesso Direto (Sem firulas de verificação que dão erro)
   
   // // Extraindo Strings
   // string user = json["usuario"].ToStr();
   // if(user != "") Print("Usuário: ", user);

   // // Extraindo Números (Se .ToDbl() falhar, tente .ToDouble())
   // double lote = json["config"]["lote"].ToDbl(); 
   // Print("Lote: ", DoubleToString(lote, 2));

   // // Extraindo Arrays
   // int totalAtivos = json["ativos"].Size();
   // if(totalAtivos > 0)
   // {
   //    for(int i = 0; i < totalAtivos; i++)
   //    {
   //       Print("Ativo [", i, "]: ", json["ativos"][i].ToStr());
   //    }
   // }

   // Extraindo Arrays
   int channels = json["channel"].Size();
   if(channels > 0)
   {
      // Para cada item dentro de 'channels'
      for(int i = 0; i < channels; i++)
      {
         // Print(json["channel"][i]["channel_name"].ToStr());

         int LineWidth = 1;

         color LineColor = clrRed;
         string HighLineName = StringFormat("%s High", json["channel"][i]["channel_name"].ToStr());
         string LowLineName = StringFormat("%s Low", json["channel"][i]["channel_name"].ToStr());

         datetime OpenTime = StringToTime(json["channel"][i]["initial"].ToStr());
         datetime CloseTime = StringToTime(json["channel"][i]["final"].ToStr());

         double ChannelHigh = json["channel"][i]["high"].ToDbl();
         double ChannelLow = json["channel"][i]["low"].ToDbl();

         CreateObject(HighLineName, ChannelHigh, ChannelHigh, OpenTime, CloseTime, LineColor, LineWidth);
         CreateObject(LowLineName, ChannelLow, ChannelLow, OpenTime, CloseTime, LineColor, LineWidth);

         // Print("Ativo [", i, "]: ", json["ativos"][i].ToStr());         
         ChartRedraw();
      }
   }
   // AbrirArquivo(flags);
}
