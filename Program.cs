using Microsoft.EntityFrameworkCore;
using AutoMapper;
using Scada;
using System;
using Npgsql;

NpgsqlConnection.GlobalTypeMapper.UseJsonNet();

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddCors();

// Add services to the container.
builder.Services.AddRouting(options => options.LowercaseUrls = true);
builder.Services.AddControllers().AddNewtonsoftJson();
// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
//builder.Services.AddDbContext<AppDbContext>(x => x.UseSqlite("Data Source=LocalDatabase.db"));
// set to your local postgresql info  
var postgresql_db = Environment.GetEnvironmentVariable("POSTGRES_DB") ?? string.Empty;
var postgresql_host = Environment.GetEnvironmentVariable("POSTGRES_HOST") ?? string.Empty;
var postgresql_user = Environment.GetEnvironmentVariable("POSTGRES_USER") ?? string.Empty;
var postgresql_password = Environment.GetEnvironmentVariable("POSTGRES_PASSWORD") ?? string.Empty;
var connection_string = $"Host={postgresql_host};Database={postgresql_db};Username={postgresql_user};Password={postgresql_password}";

builder.Services.AddDbContext<AppDbContext>(x => x.UseNpgsql(connection_string));

builder.Services.AddAutoMapper(AppDomain.CurrentDomain.GetAssemblies());
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

using (var scope = app.Services.CreateScope())
{
    var dbContext = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    dbContext.Database.EnsureCreated();
}

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(
        opt => opt.DefaultModelsExpandDepth(-1)
    );
}

// app.UseHttpsRedirection();

app.UseCors(builder =>
{
    builder
    .AllowAnyOrigin()
    .AllowAnyMethod()
    .AllowAnyHeader();
});

app.UseAuthorization();

app.MapControllers();

app.Run();
