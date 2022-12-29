using Microsoft.EntityFrameworkCore;
using AutoMapper;
using Scada;

var builder = WebApplication.CreateBuilder(args);


builder.Services.AddCors();

// Add services to the container.
builder.Services.AddRouting(options => options.LowercaseUrls = true);
builder.Services.AddControllers();
// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
//builder.Services.AddDbContext<AppDbContext>(x => x.UseSqlite("Data Source=LocalDatabase.db"));
// set to your local postgresql info
builder.Services.AddDbContext<AppDbContext>(x => x.UseNpgsql("Host=localhost;Database=scada;Username=myuser;Password=mypassword"));
builder.Services.AddAutoMapper(AppDomain.CurrentDomain.GetAssemblies());
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(
        opt => opt.DefaultModelsExpandDepth(-1)
    );
}

app.UseHttpsRedirection();

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
