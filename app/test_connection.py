from sqlalchemy import create_engine, text

try:
   
    engine = create_engine("postgresql://postgres@localhost:5432/DiarioEmocional")
    
    with engine.connect() as conn:
        
        result = conn.execute(text("SELECT version();"))
        print("✅ PostgreSQL CONECTADO en puerto 5434:")
        print(f"   {result.fetchone()[0]}")
        
        
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        
        print("📊 Tablas en la base de datos:")
        tables = [table[0] for table in result]
        
        if tables:
            for table in tables:
                print(f"   - {table}")
        else:
            print("   ℹ️  No hay tablas aún, las crearemos con SQLAlchemy")
            
        
        try:
            result = conn.execute(text("SELECT COUNT(*) FROM emociones;"))
            count = result.fetchone()[0]
            print(f"😊 Emociones en la base: {count}")
        except:
            print("😊 Tabla 'emociones' no existe aún")
            
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    print("\n💡 Posibles soluciones:")
    print("   1. Verificar que PostgreSQL esté corriendo en puerto 5434")
    print("   2. Revisar que la base de datos 'DiarioEmocional' exista")
    print("   3. Probar sin contraseña en la conexión")