FROM mcr.microsoft.com/dotnet/aspnet:5.0 AS base
WORKDIR /app
EXPOSE 80
EXPOSE 443

FROM mcr.microsoft.com/dotnet/sdk:5.0 AS build
WORKDIR /src
COPY ["SecurityBand.Lct.Api.csproj", "./"]
RUN dotnet restore "SecurityBand.Lct.Api.csproj"
COPY . .
WORKDIR "/src/"
RUN dotnet build "SecurityBand.Lct.Api.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "SecurityBand.Lct.Api.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "SecurityBand.Lct.Api.dll"]
